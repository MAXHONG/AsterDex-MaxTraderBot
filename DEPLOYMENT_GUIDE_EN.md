# SSH Server Deployment Guide

Complete guide for deploying the AsterDEX Automated Trading Bot on an SSH server.

[中文文档](SSH_DEPLOYMENT_GUIDE.md) | [English Documentation](DEPLOYMENT_GUIDE_EN.md)

## 📋 Project Information

- **Project Name**: AsterDEX Automated Trading Bot
- **GitHub Repository**: https://github.com/MAXHONG/AsterDex-MaxTraderBot
- **Features**: Automated cryptocurrency contract trading based on dual moving average strategy

## 🚀 Quick Deployment Steps

### 1. Connect to SSH Server

```bash
ssh your_username@your_server_ip
```

### 2. Clone the Project

```bash
cd ~
git clone https://github.com/MAXHONG/AsterDex-MaxTraderBot.git
cd AsterDex-MaxTraderBot
```

### 3. Run Installation Script

```bash
bash deploy/install.sh
```

The installation script will automatically:
- Check Python version (requires 3.9+)
- Create virtual environment
- Install all dependencies

### 4. Configure the Trading Bot

#### 4.1 Copy Configuration Template

```bash
cp config/config.example.json config/config.json
```

#### 4.2 Edit Configuration File

```bash
vim config/config.json
# or use nano
nano config/config.json
```

#### 4.3 Required Configuration

```json
{
  "asterdex": {
    "user": "0xYourMainWalletAddress",           // Your main wallet address
    "signer": "0xYourAPIWalletAddress",          // API wallet address
    "private_key": "0xYourAPIWalletPrivateKey",  // API wallet private key
    "api_base_url": "https://fapi.asterdex.com"
  },
  "deepseek": {
    "api_key": "sk-xxxxx",                       // DeepSeek API Key (optional)
    "api_base_url": "https://api.deepseek.com",
    "model": "deepseek-chat"
  },
  "trading": {
    "symbols": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ASTERUSDT"],
    "max_leverage": 5,
    "max_position_percent": 30,
    "margin_type": "ISOLATED"
  }
}
```

#### 4.4 Get API Keys

**AsterDEX API Wallet**:
1. Visit https://www.asterdex.com/en/api-wallet
2. Create API wallet
3. Get Signer address and private key
4. **⚠️ Important**: Keep your private key secure

**DeepSeek API** (Optional, for AI-assisted decisions):
1. Visit https://platform.deepseek.com/
2. Register and get API Key

### 5. Test Run

Before running in background, test to ensure everything works:

```bash
source venv/bin/activate
python src/main.py
```

Observe the output to ensure:
- ✅ Can connect to AsterDEX API
- ✅ Can retrieve trading pair information
- ✅ Can get K-line data
- ✅ No configuration errors

Press `Ctrl+C` to stop the test.

### 6. Deploy as System Service

```bash
bash deploy/deploy.sh
```

This will:
- Create systemd service file
- Install as system service
- Configure auto-restart

### 7. Start the Service

```bash
sudo systemctl start asterdex-bot
```

### 8. Verify Service Status

```bash
sudo systemctl status asterdex-bot
```

You should see `Active: active (running)` status.

### 9. View Real-time Logs

```bash
# System logs
sudo journalctl -u asterdex-bot -f

# Application logs
tail -f logs/trading_bot.log
```

## 📊 Service Management Commands

### Basic Operations

```bash
# Start service
sudo systemctl start asterdex-bot

# Stop service
sudo systemctl stop asterdex-bot

# Restart service
sudo systemctl restart asterdex-bot

# Check status
sudo systemctl status asterdex-bot

# Enable auto-start on boot
sudo systemctl enable asterdex-bot

# Disable auto-start
sudo systemctl disable asterdex-bot
```

### View Logs

```bash
# Real-time system logs
sudo journalctl -u asterdex-bot -f

# Recent 100 lines
sudo journalctl -u asterdex-bot -n 100

# View application logs
tail -f logs/trading_bot.log

# View complete application logs
cat logs/trading_bot.log
```

## 🔧 Configuration Details

### Trading Strategy Configuration

#### High-Frequency Strategy (15-minute K-line)

```json
{
  "strategies": {
    "high_frequency": {
      "enabled": true,
      "interval": "15m",
      "check_interval_seconds": 300,  // Check every 5 minutes
      "ma_periods": {
        "sma_short": 20,
        "sma_medium": 60,
        "sma_long": 120,
        "ema_short": 20,
        "ema_medium": 60,
        "ema_long": 120
      },
      "convergence_threshold_percent": 2.0,        // 2% convergence threshold
      "breakout_confirmation_minutes": 30          // 30-minute confirmation
    }
  }
}
```

#### Medium-Frequency Strategy (4-hour K-line)

```json
{
  "strategies": {
    "medium_frequency": {
      "enabled": true,
      "interval": "4h",
      "check_interval_seconds": 3600,  // Check every 1 hour
      "ma_periods": {
        "sma_short": 20,
        "sma_medium": 60,
        "sma_long": 120,
        "ema_short": 20,
        "ema_medium": 60,
        "ema_long": 120
      },
      "convergence_threshold_percent": 2.0,
      "breakout_confirmation_minutes": 30
    }
  }
}
```

### Risk Management Configuration

```json
{
  "risk_management": {
    "enable_stop_loss": true,
    "stop_loss_percent": 3.0,      // 3% stop loss
    "enable_take_profit": false,
    "take_profit_percent": 10.0    // 10% take profit
  }
}
```

## 🔐 Security Best Practices

### 1. Protect Configuration File

```bash
chmod 600 config/config.json
```

### 2. Use Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw enable
```

### 3. Regular Configuration Backups

```bash
cp config/config.json ~/config_backup_$(date +%Y%m%d).json
```

### 4. Monitor Log Anomalies

Regularly check logs for errors and warnings:

```bash
grep -i error logs/trading_bot.log
grep -i warning logs/trading_bot.log
```

## 📈 Monitoring and Maintenance

### Check System Resources

```bash
# CPU and memory
top -p $(pgrep -f "python src/main.py")

# Disk usage
df -h

# Log file size
du -sh logs/
```

### Update Code

```bash
# Stop service
sudo systemctl stop asterdex-bot

# Backup configuration
cp config/config.json config/config.backup.json

# Pull latest code
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restore configuration (if overwritten)
cp config/config.backup.json config/config.json

# Restart service
sudo systemctl start asterdex-bot
```

## 🐛 Troubleshooting

### Service Startup Failure

1. **Check configuration file**
```bash
python -m json.tool config/config.json
```

2. **View error logs**
```bash
sudo journalctl -u asterdex-bot -n 50 --no-pager
```

3. **Manual run for testing**
```bash
source venv/bin/activate
python src/main.py
```

### API Connection Failure

1. **Test network connection**
```bash
curl -I https://fapi.asterdex.com/fapi/v1/ping
```

2. **Check time synchronization**
```bash
timedatectl status
```

3. **Sync system time**
```bash
sudo timedatectl set-ntp true
```

### Signature Errors

Signature errors are usually caused by time desynchronization:

```bash
# Check time
date
timedatectl

# Sync time
sudo ntpdate -s time.nist.gov
# or
sudo timedatectl set-ntp true
```

### Memory Issues

```bash
# Check memory
free -h

# Clear cache
sudo sync && sudo sysctl -w vm.drop_caches=3
```

## 📞 Support

If you encounter issues:

1. Check [README_EN.md](README_EN.md) documentation
2. Check [deploy/DEPLOYMENT.md](deploy/DEPLOYMENT.md) for detailed deployment guide
3. Check log files for error causes
4. Submit an issue on GitHub: https://github.com/MAXHONG/AsterDex-MaxTraderBot/issues

## ⚠️ Disclaimer

- This software is for educational and research purposes only
- Cryptocurrency trading involves high risk
- Fully understand the risks before use
- Test with small amounts first
- The developer is not responsible for any trading losses

## 📝 License

MIT License

---

**Developer**: MAXHONG  
**Project URL**: https://github.com/MAXHONG/AsterDex-MaxTraderBot  
**Last Updated**: 2025-10-22

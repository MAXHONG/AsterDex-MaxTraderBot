# AsterDEX Automated Trading Bot

An automated trading bot based on AsterDEX API with dual moving average strategy, supporting BTC, ETH, BNB, and ASTER contract trading.

[中文文档](README.md) | [English Documentation](README_EN.md)

## ✨ Features

- ✅ **Dual Moving Average Strategy**: Based on SMA20/60/120 and EMA20/60/120
- ✅ **Multi-Frequency Trading**:
  - High-frequency: 15-minute K-line, check every 5 minutes
  - Medium-frequency: 4-hour K-line, check every 1 hour
- ✅ **AI-Assisted Decision Making**: Integrated with DeepSeek AI for trading signal confirmation
- ✅ **Risk Management**: Isolated margin mode, max 5x leverage, single coin max 30% margin usage
- ✅ **Multi-Coin Support**: BTC/USDT, ETH/USDT, BNB/USDT, ASTER/USDT

## 📋 Trading Strategy

### Dual Moving Average Convergence Detection

When short-term (SMA20/EMA20), medium-term (SMA60/EMA60), and long-term (SMA120/EMA120) moving averages converge in price range:

**Long Position Conditions**:
1. Moving averages converge
2. Price breaks above moving averages
3. Price stays above moving averages for 30 minutes
4. Open long position

**Short Position Conditions**:
1. Moving averages converge
2. Price breaks below moving averages
3. Price stays below moving averages for 30 minutes
4. Open short position

**Close Position**:
- Close position when moving averages converge again

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip
- git
- sudo privileges (for system service installation)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/MAXHONG/AsterDex-MaxTraderBot.git
cd AsterDex-MaxTraderBot
```

#### 2. Run Installation Script

```bash
bash deploy/install.sh
```

This will:
- Check Python version
- Create virtual environment
- Install all dependencies

#### 3. Configure the Bot

Copy the configuration template:

```bash
cp config/config.example.json config/config.json
```

Edit the configuration file:

```bash
vim config/config.json
# or
nano config/config.json
```

Required configuration:

```json
{
  "asterdex": {
    "user": "YourMainWalletAddress",
    "signer": "APIWalletAddress",
    "private_key": "APIWalletPrivateKey"
  },
  "deepseek": {
    "api_key": "YourDeepSeekAPIKey"
  },
  "trading": {
    "symbols": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ASTERUSDT"],
    "max_leverage": 5,
    "max_position_percent": 30
  }
}
```

#### 4. Test Run

```bash
source venv/bin/activate
python src/main.py
```

Press `Ctrl+C` to stop.

#### 5. Deploy as System Service

```bash
bash deploy/deploy.sh
```

#### 6. Start the Service

```bash
sudo systemctl start asterdex-bot
```

## 🔑 Getting API Keys

### AsterDEX API Wallet
1. Visit https://www.asterdex.com/en/api-wallet
2. Create an API wallet
3. Get Signer address and private key
4. **⚠️ Important**: Keep your private key secure

### DeepSeek API (Optional)
1. Visit https://platform.deepseek.com/
2. Register and get API Key

## 📊 Service Management

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

# Application logs
tail -f logs/trading_bot.log
```

## 🛠️ Project Structure

```
AsterDex-MaxTraderBot/
├── src/
│   ├── main.py                 # Main entry point
│   ├── api/
│   │   ├── asterdex_client.py  # AsterDEX API client
│   │   └── deepseek_client.py  # DeepSeek API client
│   ├── strategies/
│   │   ├── double_ma.py        # Dual MA strategy
│   │   └── indicators.py       # Technical indicators
│   ├── trading/
│   │   ├── trader.py           # Trading executor
│   │   └── risk_manager.py     # Risk management
│   └── utils/
│       ├── logger.py           # Logging utility
│       └── config.py           # Configuration loader
├── config/
│   ├── config.json             # Configuration file
│   └── config.example.json     # Configuration template
├── logs/                       # Log directory
├── tests/                      # Test files
├── deploy/
│   └── asterdex-bot.service    # Systemd service
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

## ⚙️ Configuration

### Trading Strategy Configuration

#### High-Frequency Strategy (15-minute K-line)

```json
{
  "strategies": {
    "high_frequency": {
      "enabled": true,
      "interval": "15m",
      "check_interval_seconds": 300,
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

#### Medium-Frequency Strategy (4-hour K-line)

```json
{
  "strategies": {
    "medium_frequency": {
      "enabled": true,
      "interval": "4h",
      "check_interval_seconds": 3600,
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

### Risk Management

```json
{
  "risk_management": {
    "enable_stop_loss": true,
    "stop_loss_percent": 3.0,
    "enable_take_profit": false,
    "take_profit_percent": 10.0
  }
}
```

## 🔐 Security Recommendations

### 1. Protect Configuration File

```bash
chmod 600 config/config.json
```

### 2. Use Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw enable
```

### 3. Regular Backups

```bash
cp config/config.json ~/config_backup_$(date +%Y%m%d).json
```

### 4. Monitor Logs

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

# Restore configuration
cp config/config.backup.json config/config.json

# Restart service
sudo systemctl start asterdex-bot
```

## 🐛 Troubleshooting

### Service Fails to Start

1. **Check configuration file**
```bash
python -m json.tool config/config.json
```

2. **View error logs**
```bash
sudo journalctl -u asterdex-bot -n 50 --no-pager
```

3. **Run manually for testing**
```bash
source venv/bin/activate
python src/main.py
```

### API Connection Failed

1. **Test network connection**
```bash
curl -I https://fapi.asterdex.com
```

2. **Check API keys are correct**

3. **Check firewall settings**

### Signature Errors

Signature errors are usually caused by time synchronization issues:

```bash
# Check time
date
timedatectl

# Sync time
sudo timedatectl set-ntp true
```

### Memory Issues

```bash
# Check memory
free -h

# Clear cache if needed
sudo sync && sudo sysctl -w vm.drop_caches=3
```

## 📞 Support

If you encounter issues:

1. Check [SSH_DEPLOYMENT_GUIDE.md](SSH_DEPLOYMENT_GUIDE.md) for detailed instructions
2. Check log files for error messages
3. Refer to the documentation
4. Submit an issue on GitHub: https://github.com/MAXHONG/AsterDex-MaxTraderBot/issues

## ⚠️ Disclaimer

- This software is for educational and research purposes only
- Cryptocurrency trading involves high risk
- Use at your own risk
- Test with small amounts first
- The developer is not responsible for any trading losses

## 📝 License

MIT License

---

**Developer**: MAXHONG  
**Repository**: https://github.com/MAXHONG/AsterDex-MaxTraderBot  
**Last Updated**: 2025-10-22

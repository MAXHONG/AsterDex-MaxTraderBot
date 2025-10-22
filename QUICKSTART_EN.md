# Quick Start Guide

Get your AsterDEX trading bot up and running in 5 minutes!

[中文文档](QUICKSTART.md) | [English Documentation](QUICKSTART_EN.md)

## 🚀 5-Step Quick Deployment

### Step 1: Clone the Project

```bash
git clone https://github.com/MAXHONG/AsterDex-MaxTraderBot.git
cd AsterDex-MaxTraderBot
```

### Step 2: Install Dependencies

```bash
bash deploy/install.sh
```

This will automatically:
- ✅ Check Python version (requires 3.9+)
- ✅ Create virtual environment
- ✅ Install all required packages

### Step 3: Configure API Keys

```bash
# Copy configuration template
cp config/config.example.json config/config.json

# Edit configuration
vim config/config.json
```

**Minimal required configuration:**

```json
{
  "asterdex": {
    "user": "0xYourMainWalletAddress",
    "signer": "0xYourAPIWalletAddress",
    "private_key": "0xYourAPIWalletPrivateKey"
  },
  "trading": {
    "symbols": ["BTCUSDT", "ETHUSDT"],
    "max_leverage": 5,
    "max_position_percent": 30
  }
}
```

**Get API Keys:**
- AsterDEX: https://www.asterdex.com/en/api-wallet
- DeepSeek (optional): https://platform.deepseek.com/

### Step 4: Test Run

```bash
source venv/bin/activate
python src/main.py
```

**Expected output:**
```
2025-10-22 10:30:00 - trading_bot - INFO - ============================================================
2025-10-22 10:30:00 - trading_bot - INFO - AsterDEX Automated Trading Bot Startup
2025-10-22 10:30:00 - trading_bot - INFO - ============================================================
2025-10-22 10:30:01 - trading_bot - INFO - Successfully retrieved exchange information
2025-10-22 10:30:01 - trading_bot - INFO - AsterDEX API connection normal
```

Press `Ctrl+C` to stop.

### Step 5: Deploy as Service

```bash
bash deploy/deploy.sh
sudo systemctl start asterdex-bot
```

**Check status:**
```bash
sudo systemctl status asterdex-bot
```

## ✅ Verification

### Check Service is Running

```bash
sudo systemctl status asterdex-bot
```

Expected output:
```
● asterdex-bot.service - AsterDEX Trading Bot
   Loaded: loaded (/etc/systemd/system/asterdex-bot.service; enabled)
   Active: active (running) since...
```

### View Real-time Logs

```bash
# System logs
sudo journalctl -u asterdex-bot -f

# Application logs
tail -f logs/trading_bot.log
```

## 📊 Basic Operations

### Start/Stop/Restart Service

```bash
# Start
sudo systemctl start asterdex-bot

# Stop
sudo systemctl stop asterdex-bot

# Restart
sudo systemctl restart asterdex-bot
```

### Enable/Disable Auto-start

```bash
# Enable auto-start on boot
sudo systemctl enable asterdex-bot

# Disable auto-start
sudo systemctl disable asterdex-bot
```

## 🎯 Trading Strategy Overview

### High-Frequency Strategy
- **K-line Period**: 15 minutes
- **Check Frequency**: Every 5 minutes
- **Moving Averages**: SMA/EMA 20, 60, 120
- **Entry**: Price breaks through converged MAs and stays for 30 minutes
- **Exit**: MAs converge again

### Medium-Frequency Strategy
- **K-line Period**: 4 hours
- **Check Frequency**: Every 1 hour
- **Moving Averages**: SMA/EMA 20, 60, 120
- **Entry**: Price breaks through converged MAs and stays for 30 minutes
- **Exit**: MAs converge again

## 🔐 Important Security Notes

### 1. Protect Your Private Keys
```bash
chmod 600 config/config.json
```

### 2. Never Share Your Configuration
- ⚠️ Do not commit `config.json` to Git
- ⚠️ Do not share private keys with anyone
- ⚠️ Use API wallets with limited permissions

### 3. Start with Small Amounts
- 💰 Test with minimal funds first
- 📊 Monitor performance for a few days
- 📈 Gradually increase if satisfied

## 📋 Common Configuration Options

### Adjust Check Frequency

```json
{
  "strategies": {
    "high_frequency": {
      "check_interval_seconds": 300  // 5 minutes (300 seconds)
    },
    "medium_frequency": {
      "check_interval_seconds": 3600  // 1 hour (3600 seconds)
    }
  }
}
```

### Adjust Risk Parameters

```json
{
  "trading": {
    "max_leverage": 3,           // Reduce to 3x leverage
    "max_position_percent": 20   // Use only 20% of margin
  }
}
```

### Enable/Disable Strategies

```json
{
  "strategies": {
    "high_frequency": {
      "enabled": false  // Disable high-frequency strategy
    },
    "medium_frequency": {
      "enabled": true   // Keep medium-frequency enabled
    }
  }
}
```

## 🐛 Quick Troubleshooting

### Problem: Service won't start

**Solution:**
```bash
# Check logs for errors
sudo journalctl -u asterdex-bot -n 50

# Validate configuration
python -m json.tool config/config.json

# Try manual run
source venv/bin/activate
python src/main.py
```

### Problem: Signature errors

**Solution:**
```bash
# Sync system time
sudo timedatectl set-ntp true
timedatectl status
```

### Problem: API connection failed

**Solution:**
```bash
# Test connectivity
curl -I https://fapi.asterdex.com

# Check firewall
sudo ufw status
```

## 📞 Get Help

- **Documentation**: Check [README_EN.md](README_EN.md)
- **Deployment Guide**: See [DEPLOYMENT_GUIDE_EN.md](DEPLOYMENT_GUIDE_EN.md)
- **GitHub Issues**: https://github.com/MAXHONG/AsterDex-MaxTraderBot/issues

## 🎉 Next Steps

Once your bot is running successfully:

1. ✅ Monitor logs for the first few hours
2. ✅ Check account balance and positions regularly
3. ✅ Adjust strategy parameters based on performance
4. ✅ Set up additional monitoring (optional)

## ⚠️ Disclaimer

- Cryptocurrency trading involves high risk
- This bot is for educational purposes
- Always test with small amounts first
- The developer is not responsible for trading losses
- Understand the risks before using

---

**Happy Trading!** 🚀

**Repository**: https://github.com/MAXHONG/AsterDex-MaxTraderBot  
**Developer**: MAXHONG

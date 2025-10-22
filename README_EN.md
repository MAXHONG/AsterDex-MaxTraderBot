# AsterDEX Automated Trading Bot

An automated trading bot based on AsterDEX API with dual moving average strategy, supporting BTC, ETH, BNB, and ASTER contract trading.

[中文文档](README.md) | [English Documentation](README_EN.md)

## ✨ Features

- ✅ **Dual Moving Average Strategy**: Based on SMA20/60/120 and EMA20/60/120
- ✅ **Multi-Frequency Trading**:
  - High-frequency: 15-minute K-line, check every 5 minutes
  - Medium-frequency: 4-hour K-line, check every 1 hour
- ✅ **AI Enhancement System**: Dual AI provider support (DeepSeek/Grok), 4-phase intelligent enhancement
  - 🧠 Phase 1: Market Intelligence (Multi-source aggregation)
  - 📊 Phase 2: Dynamic Risk Assessment (Multi-dimensional analysis)
  - 🎯 Phase 3: Intelligent Position Management (Real-time optimization)
  - ⚙️ Phase 4: Strategy Parameter Optimization (Adaptive tuning)
- ✅ **Risk Management**: Isolated margin mode, max 5x leverage, single coin max 30% margin usage
- ✅ **Multi-Coin Support**: BTC/USDT, ETH/USDT, BNB/USDT, ASTER/USDT
- ✅ **Docker Support**: Containerized deployment, one-click start

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

### Deployment Methods

| Method | Use Case | Documentation |
|--------|----------|---------------|
| **🐳 Docker (Recommended)** | Quick deployment, isolated environment | [Docker Deployment Guide](DOCKER_DEPLOYMENT_EN.md) |
| **🖥️ Traditional** | Direct server deployment | [Deployment Guide](DEPLOYMENT_GUIDE_EN.md) |
| **💻 Local Development** | Development and testing | See below |

### Method 1: Docker Deployment (Recommended) ⭐

**Prerequisites**: Docker and Docker Compose installed

```bash
# 1. Clone repository
git clone https://github.com/MAXHONG/AsterDex-MaxTraderBot.git
cd AsterDex-MaxTraderBot/asterdex-trading-bot

# 2. Configure
cp config/config.example.json config/config.json
nano config/config.json  # Fill in your API keys

# 3. Start container
docker compose up -d

# 4. View logs
docker compose logs -f
```

Detailed docs: [Docker Deployment Guide](DOCKER_DEPLOYMENT_EN.md) | [Docker 部署指南 (CN)](DOCKER_DEPLOYMENT.md)

### Method 2: Traditional Deployment

#### 1. Install Dependencies

```bash
# Clone repository
git clone https://github.com/MAXHONG/AsterDex-MaxTraderBot.git
cd AsterDex-MaxTraderBot/asterdex-trading-bot

# Install Python dependencies
pip install -r requirements.txt
```

#### 2. Configure

Copy configuration template and edit:

```bash
cp config/config.example.json config/config.json
nano config/config.json
```

Edit `config/config.json`:

```json
{
  "asterdex": {
    "user": "your_main_wallet_address",
    "signer": "api_wallet_address",
    "private_key": "api_wallet_private_key",
    "api_base_url": "https://fapi.asterdex.com"
  },
  "ai": {
    "provider": "deepseek",  // or "grok"
    "deepseek": {
      "api_key": "your_deepseek_api_key",
      "api_base_url": "https://api.deepseek.com",
      "model": "deepseek-chat"
    }
  },
  "trading": {
    "symbols": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ASTERUSDT"],
    "max_leverage": 5,
    "max_position_percent": 30,
    "margin_type": "ISOLATED"
  },
  "strategies": {
    "high_frequency": {
      "enabled": true,
      "interval": "15m",
      "check_interval": 300
    },
    "medium_frequency": {
      "enabled": true,
      "interval": "4h",
      "check_interval": 3600
    }
  }
}
```

#### 3. Get API Keys

**AsterDEX API Wallet**
- Visit https://www.asterdex.com/en/api-wallet
- Create API wallet and get Signer address and private key

**AI Provider (Choose one)**
- **DeepSeek**: https://platform.deepseek.com/ (Recommended)
- **Grok**: https://console.x.ai/

#### 4. Run

**Development mode**:
```bash
python src/main.py
```

**Production mode (systemd)**:
```bash
# Install system service
sudo cp deploy/asterdex-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable asterdex-bot
sudo systemctl start asterdex-bot

# View logs
sudo journalctl -u asterdex-bot -f
```

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

## 📁 Project Structure

```
asterdex-trading-bot/
├── src/
│   ├── main.py                      # Main entry point
│   ├── api/
│   │   ├── base_ai_client.py        # AI client base (DeepSeek/Grok)
│   │   ├── asterdex_client.py       # AsterDEX API client
│   │   └── deepseek_client.py       # DeepSeek client (deprecated)
│   ├── ai/                          # AI Enhancement System
│   │   ├── market_intelligence.py   # Phase 1: Market Intelligence
│   │   ├── risk_assessor.py         # Phase 2: Risk Assessment
│   │   ├── position_manager.py      # Phase 3: Position Management
│   │   └── parameter_optimizer.py   # Phase 4: Parameter Optimization
│   ├── strategies/
│   │   ├── double_ma.py             # Dual MA strategy
│   │   └── indicators.py            # Technical indicators
│   ├── trading/
│   │   ├── trader.py                # Trading executor
│   │   └── risk_manager.py          # Risk management
│   └── utils/
│       ├── logger.py                # Logging utility
│       └── config.py                # Configuration loader
├── config/
│   ├── config.json                  # Configuration file
│   └── config.example.json          # Configuration template
├── logs/                            # Log directory
├── tests/                           # Test files
├── deploy/
│   └── asterdex-bot.service         # Systemd service file
├── Dockerfile                       # Docker image build
├── docker-compose.yml               # Docker Compose config
├── .dockerignore                    # Docker ignore file
├── requirements.txt                 # Python dependencies
└── README.md                        # Project documentation
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

## 📚 Complete Documentation

| Document | Description | Language |
|----------|-------------|----------|
| [README.md](README.md) | Project README | 🇨🇳 Chinese |
| [README_EN.md](README_EN.md) | Project README | 🇬🇧 English |
| [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) | Docker Deployment | 🇨🇳 Chinese |
| [DOCKER_DEPLOYMENT_EN.md](DOCKER_DEPLOYMENT_EN.md) | Docker Deployment | 🇬🇧 English |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Deployment Guide | 🇨🇳 Chinese |
| [DEPLOYMENT_GUIDE_EN.md](DEPLOYMENT_GUIDE_EN.md) | Deployment Guide | 🇬🇧 English |
| [AI_ENHANCEMENT_IMPLEMENTATION_COMPLETE.md](AI_ENHANCEMENT_IMPLEMENTATION_COMPLETE.md) | AI Enhancement | 🇨🇳 Chinese |

## 🤖 AI Enhancement System

This project integrates a complete AI enhancement system with four phases:

- **Phase 1**: Market Intelligence System (Multi-source aggregation)
- **Phase 2**: Dynamic Risk Assessment (Multi-dimensional analysis)
- **Phase 3**: Intelligent Position Management (Real-time optimization)
- **Phase 4**: Strategy Parameter Optimization (Adaptive tuning)

**Expected Performance**: +35-55% overall improvement

See: [AI_ENHANCEMENT_IMPLEMENTATION_COMPLETE.md](AI_ENHANCEMENT_IMPLEMENTATION_COMPLETE.md)

## 📞 Support

If you encounter issues:
1. Check the relevant documentation guide
2. Check log files for detailed error messages
3. Submit an issue: https://github.com/MAXHONG/AsterDex-MaxTraderBot/issues

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

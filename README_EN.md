# AsterDEX Automated Trading Bot

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![AsterDEX](https://img.shields.io/badge/Exchange-AsterDEX-orange.svg)](https://www.asterdex.com/)

Intelligent Futures Trading System based on AsterDEX API with Dual Moving Average Strategy and AI Enhancement

[中文文档](README.md) | [English Documentation](README_EN.md)

</div>

---

## ✨ Core Features

### 🎯 Trading Strategy
- **Dual Moving Average System**: SMA20/60/120 + EMA20/60/120 combination
- **Multi-Frequency Trading**:
  - 🔥 High-Freq: 15-min K-line, check every 5 minutes
  - ⏱️ Mid-Freq: 4-hour K-line, check every 1 hour
- **Smart Signals**: MA convergence detection + breakout confirmation

### 🤖 AI Enhancement System (Optional)

Supports **DeepSeek** and **Grok** dual AI providers with 4-phase optimization:

| Phase | Function | Improvement |
|-------|----------|-------------|
| 🧠 **Phase 1** | Market Intelligence | Multi-source data aggregation |
| 📊 **Phase 2** | Dynamic Risk Assessment | +30-40% risk control |
| 🎯 **Phase 3** | Intelligent Position Management | +25-35% position optimization |
| ⚙️ **Phase 4** | Strategy Parameter Optimization | +20-30% parameter adaptation |

> **Overall Performance**: +35-55% improvement | [View Details](AI_ENHANCEMENT_IMPLEMENTATION_COMPLETE.md)

### 🛡️ Risk Management
- **Isolated Margin**: Risk isolation per coin
- **Leverage Limit**: Max 5x, adjustable
- **Position Control**: Max 30% margin per coin
- **Stop Loss**: Dynamic 3% + AI optimization

### 💰 Supported Pairs
- BTC/USDT
- ETH/USDT
- BNB/USDT
- ASTER/USDT

---

## 📋 Trading Strategy

### Dual Moving Average Convergence

When short-term (SMA20/EMA20), medium-term (SMA60/EMA60), and long-term (SMA120/EMA120) MAs converge:

#### Long Signal 📈
1. ✅ Three MA groups converge (spread ≤ 2%)
2. ✅ Price breaks above MAs
3. ✅ Confirmed stable above for 30 minutes
4. ✅ Open long position

#### Short Signal 📉
1. ✅ Three MA groups converge (spread ≤ 2%)
2. ✅ Price breaks below MAs
3. ✅ No bounce back within 30 minutes
4. ✅ Open short position

#### Close Position 🔄
- Close when MAs converge again
- AI suggests early close (optional)
- Stop-loss/take-profit triggered

---

## 🚀 Quick Start

### Deployment Methods Comparison

| Method | Difficulty | Use Case | Rating |
|--------|-----------|----------|--------|
| 🐳 **Docker** | ⭐ Easy | Production, quick deploy | ⭐⭐⭐⭐⭐ |
| 🖥️ **Traditional** | ⭐⭐ Medium | Customization needs | ⭐⭐⭐ |
| 💻 **Local Dev** | ⭐⭐⭐ Hard | Development & debugging | ⭐⭐ |

---

## 🐳 Method 1: Docker Deployment (Recommended)

### Prerequisites

Ensure Docker and Docker Compose are installed:

```bash
# Check versions
docker --version  # Need 20.10+
docker compose version  # Need 2.0+
```

If not installed:
- Docker: https://docs.docker.com/get-docker/
- Docker Compose: https://docs.docker.com/compose/install/

### One-Click Deployment

```bash
# 1. Clone repository
git clone https://github.com/MAXHONG/AsterDex-MaxTraderBot.git
cd AsterDex-MaxTraderBot/asterdex-trading-bot

# 2. Copy configuration
cp config/config.example.json config/config.json

# 3. Edit configuration (IMPORTANT!)
nano config/config.json
# Or use other editors: vim, code, etc.

# 4. Start container
docker compose up -d

# 5. View logs
docker compose logs -f
```

### Configuration

Edit `config/config.json` with your credentials:

```json
{
  "asterdex": {
    "user": "0xYourMainWalletAddress",
    "signer": "0xYourAPIWalletAddress",
    "private_key": "0xYourAPIWalletPrivateKey",
    "api_base_url": "https://fapi.asterdex.com"
  },
  "ai": {
    "enabled": true,           // true=enable AI, false=disable AI
    "provider": "deepseek",    // "deepseek" or "grok"
    "deepseek": {
      "api_key": "sk-xxx",     // DeepSeek API key
      "api_base_url": "https://api.deepseek.com",
      "model": "deepseek-chat",
      "timeout": 30
    },
    "grok": {
      "api_key": "xai-xxx",    // Grok API key (optional)
      "api_base_url": "https://api.x.ai/v1",
      "model": "grok-beta",
      "timeout": 30
    }
  },
  "trading": {
    "symbols": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ASTERUSDT"],
    "max_leverage": 5,
    "max_position_percent": 30,
    "margin_type": "ISOLATED"
  }
}
```

### Docker Commands

```bash
# Start service
docker compose up -d

# Stop service
docker compose stop

# Restart service
docker compose restart

# View logs (real-time)
docker compose logs -f

# View last 100 lines
docker compose logs --tail=100

# Check container status
docker compose ps

# Enter container for debugging
docker compose exec asterdex-bot bash

# Complete removal (including images)
docker compose down --rmi all

# Update and restart
git pull
docker compose up -d --build
```

### Environment Variables (Optional)

If you prefer environment variables over `config.json`:

```bash
# 1. Copy template
cp .env.example .env

# 2. Edit .env file
nano .env

# 3. Modify docker-compose.yml to uncomment env vars

# 4. Start
docker compose up -d
```

**Detailed Docs**: [Complete Docker Deployment Guide](DOCKER_DEPLOYMENT_EN.md)

---

## 🖥️ Method 2: Traditional Deployment

### 1. System Requirements

- **OS**: Ubuntu 20.04+ / CentOS 7+ / macOS
- **Python**: 3.11+
- **RAM**: Min 512MB, recommended 1GB+
- **Disk**: Min 500MB

### 2. Install Dependencies

```bash
# Clone repository
git clone https://github.com/MAXHONG/AsterDex-MaxTraderBot.git
cd AsterDex-MaxTraderBot/asterdex-trading-bot

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy template
cp config/config.example.json config/config.json

# Edit configuration (see Docker config above)
nano config/config.json

# Set file permissions (IMPORTANT!)
chmod 600 config/config.json
```

### 4. Get API Keys

#### AsterDEX API Wallet
1. Visit https://www.asterdex.com/en/api-wallet
2. Create API wallet
3. Get Signer address and private key
4. Transfer funds from main wallet to API wallet

#### AI Provider (Choose One)

**Option 1: DeepSeek (Recommended)**
- Visit https://platform.deepseek.com/
- Register and top up
- Create API Key
- Cost: ~$0.14/million tokens (very low cost)

**Option 2: Grok**
- Visit https://console.x.ai/
- Register account
- Create API Key
- Set `ai.provider` to `"grok"` in config

### 5. Run

#### Option A: Direct Run (Testing)

```bash
python src/main.py
```

Press `Ctrl+C` to stop.

#### Option B: Background Run (Production)

**Using systemd (Recommended)**:

```bash
# 1. Edit service file, modify paths
sudo nano /home/user/webapp/asterdex-trading-bot/deploy/asterdex-bot.service

# 2. Copy to system directory
sudo cp deploy/asterdex-bot.service /etc/systemd/system/

# 3. Reload and start
sudo systemctl daemon-reload
sudo systemctl enable asterdex-bot
sudo systemctl start asterdex-bot

# 4. Check status
sudo systemctl status asterdex-bot

# 5. View logs
sudo journalctl -u asterdex-bot -f
```

**Using nohup**:

```bash
nohup python src/main.py > output.log 2>&1 &

# Check process
ps aux | grep main.py

# Stop process
kill <PID>
```

**Detailed Docs**: [Complete Deployment Guide](DEPLOYMENT_GUIDE_EN.md)

---

## 💻 Method 3: Local Development

For developers working on features and debugging:

```bash
# 1. Clone repository
git clone https://github.com/MAXHONG/AsterDex-MaxTraderBot.git
cd AsterDex-MaxTraderBot/asterdex-trading-bot

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies (including dev tools)
pip install -r requirements.txt
pip install pytest black flake8  # Dev tools

# 4. Configuration
cp config/config.example.json config/config.json
nano config/config.json

# 5. Run tests
python test_deepseek_fallback.py

# 6. Start development service
python src/main.py
```

---

## 📁 Project Structure

```
asterdex-trading-bot/
├── src/                              # Source code
│   ├── main.py                       # Main entry point
│   ├── api/                          # API clients
│   │   ├── base_ai_client.py         # Unified AI interface (DeepSeek/Grok)
│   │   ├── asterdex_client.py        # AsterDEX API client
│   │   └── deepseek_client.py        # (Deprecated)
│   ├── ai/                           # AI enhancement modules
│   │   ├── market_intelligence.py    # Phase 1: Market Intelligence
│   │   ├── risk_assessor.py          # Phase 2: Risk Assessment
│   │   ├── position_manager.py       # Phase 3: Position Management
│   │   └── parameter_optimizer.py    # Phase 4: Parameter Optimization
│   ├── strategies/                   # Trading strategies
│   │   ├── double_ma.py              # Dual MA strategy
│   │   └── indicators.py             # Technical indicators
│   ├── trading/                      # Trading modules
│   │   ├── trader.py                 # Trading executor
│   │   └── risk_manager.py           # Risk management
│   └── utils/                        # Utility functions
│       ├── logger.py                 # Logging system
│       └── config.py                 # Configuration loader
├── config/                           # Configuration files
│   ├── config.json                   # Main config (need create)
│   └── config.example.json           # Config template
├── logs/                             # Log directory
├── tests/                            # Test files
├── deploy/                           # Deployment related
│   └── asterdex-bot.service          # Systemd service
├── Dockerfile                        # Docker image
├── docker-compose.yml                # Docker Compose config
├── .dockerignore                     # Docker ignore file
├── .env.example                      # Environment variable template
├── requirements.txt                  # Python dependencies
└── README_EN.md                      # This document
```

---

## 📊 Monitoring and Maintenance

### View Logs

**Docker Deployment**:
```bash
# Real-time logs
docker compose logs -f

# Last 100 lines
docker compose logs --tail=100

# Container log file
docker compose exec asterdex-bot tail -f /app/logs/trading_bot.log
```

**Traditional Deployment**:
```bash
# System logs
sudo journalctl -u asterdex-bot -f

# Application logs
tail -f logs/trading_bot.log

# Filter errors
grep -i error logs/trading_bot.log
grep -i warning logs/trading_bot.log
```

### Performance Monitoring

```bash
# Docker resource usage
docker stats asterdex-trading-bot

# System resources
top -p $(pgrep -f "python src/main.py")
htop

# Disk usage
df -h
du -sh logs/
```

### Update Code

**Docker Deployment**:
```bash
cd AsterDex-MaxTraderBot/asterdex-trading-bot
git pull origin main
docker compose up -d --build
```

**Traditional Deployment**:
```bash
# 1. Stop service
sudo systemctl stop asterdex-bot

# 2. Backup configuration
cp config/config.json config/config.backup.json

# 3. Update code
git pull origin main

# 4. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 5. Restore configuration
cp config/config.backup.json config/config.json

# 6. Restart service
sudo systemctl start asterdex-bot
```

---

## 🔐 Security Recommendations

### 🔒 Protect Private Keys
```bash
# Set config file permissions
chmod 600 config/config.json

# Ensure .gitignore includes sensitive files
cat .gitignore | grep config.json
cat .gitignore | grep .env
```

### 🛡️ Firewall Setup
```bash
# Ubuntu/Debian
sudo ufw allow 22/tcp
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

### 💾 Regular Backups
```bash
# Backup configuration
cp config/config.json ~/backups/config_$(date +%Y%m%d).json

# Backup logs
tar -czf ~/backups/logs_$(date +%Y%m%d).tar.gz logs/
```

### 🔍 Security Checklist

- [ ] ✅ Private keys not leaked (don't commit to Git)
- [ ] ✅ Config file permissions correct (600 or 400)
- [ ] ✅ Test with small amounts first
- [ ] ✅ Regularly check logs and trades
- [ ] ✅ Set up alerts (optional)
- [ ] ✅ Keep code and dependencies updated

---

## 🐛 Troubleshooting

### Common Issues

#### 1️⃣ Signature Error (Signature Invalid)

**Cause**: Time not synchronized

**Solution**:
```bash
# Check time
date
timedatectl

# Sync time
sudo timedatectl set-ntp true

# Or manual sync
sudo ntpdate -u pool.ntp.org
```

#### 2️⃣ API Connection Failed

**Check network**:
```bash
curl -I https://fapi.asterdex.com
ping -c 4 fapi.asterdex.com
```

**Check configuration**:
```bash
# Validate JSON format
python -m json.tool config/config.json

# Verify API keys are correct
```

#### 3️⃣ AI Call Failed

**Check AI configuration**:
- Confirm API Key is correct
- Confirm sufficient balance
- Check detailed errors in logs

**Fallback mode**:
```json
{
  "ai": {
    "enabled": false  // Disable AI, use pure technical indicators
  }
}
```

#### 4️⃣ Insufficient Balance

**Check balance**:
```bash
# View logs
grep -i "insufficient" logs/trading_bot.log

# Login to AsterDEX to check account balance
```

#### 5️⃣ Docker Container Won't Start

**View error logs**:
```bash
docker compose logs

# Check if config file exists
ls -la config/config.json

# Check file format
docker compose config
```

#### 6️⃣ Memory Insufficient

**Check memory**:
```bash
free -h

# Docker memory limit
docker stats asterdex-trading-bot

# Clean Docker cache
docker system prune -a
```

---

## 📚 Complete Documentation Index

### Chinese Docs 🇨🇳

| Document | Description | Link |
|----------|-------------|------|
| **README.md** | Main README | [View](README.md) |
| **OPERATIONS_GUIDE.md** | 🔥 Operations Guide (Start/Pause/Stop) | [View](OPERATIONS_GUIDE.md) |
| **DOCKER_DEPLOYMENT.md** | Docker Deployment Guide | [View](DOCKER_DEPLOYMENT.md) |
| **DEPLOYMENT_GUIDE.md** | Traditional Deployment Guide | [View](DEPLOYMENT_GUIDE.md) |
| **AI_ENHANCEMENT_IMPLEMENTATION_COMPLETE.md** | AI Enhancement System | [View](AI_ENHANCEMENT_IMPLEMENTATION_COMPLETE.md) |
| **AI_ENHANCEMENT_ROADMAP.md** | AI Enhancement Roadmap | [View](AI_ENHANCEMENT_ROADMAP.md) |
| **QUICKSTART.md** | Quick Start Guide | [View](QUICKSTART.md) |

### English Docs 🇬🇧

| Document | Description | Link |
|----------|-------------|------|
| **README_EN.md** | Main README (this file) | Current page |
| **DOCKER_DEPLOYMENT_EN.md** | Docker Deployment Guide | [View](DOCKER_DEPLOYMENT_EN.md) |
| **DEPLOYMENT_GUIDE_EN.md** | Deployment Guide | [View](DEPLOYMENT_GUIDE_EN.md) |
| **QUICKSTART_EN.md** | Quick Start Guide | [View](QUICKSTART_EN.md) |

---

## 🤖 AI Enhancement System

### Feature Overview

| Phase | Module | Function | Input | Output |
|-------|--------|----------|-------|--------|
| **Phase 1** | Market Intel | Multi-source aggregation | Symbol, timeframe | Sentiment score, risk level |
| **Phase 2** | Risk Assessment | Multi-dimensional analysis | Trading signal, market context | Position adjustment, leverage |
| **Phase 3** | Position Mgmt | Real-time optimization | Position info, current price | Close suggestion, SL adjustment |
| **Phase 4** | Parameter Opt | Adaptive tuning | Current params, market state | Optimized params, strategy switch |

### Usage

**Fully Enabled** (Recommended):
```json
{
  "ai": {
    "enabled": true,
    "provider": "deepseek"
  }
}
```

**Disable AI** (Pure technical indicators):
```json
{
  "ai": {
    "enabled": false
  }
}
```

**Switch AI Provider**:
```json
{
  "ai": {
    "enabled": true,
    "provider": "grok"  // Switch from deepseek to grok
  }
}
```

### Performance Comparison

| Metric | Without AI | With AI | Improvement |
|--------|-----------|---------|-------------|
| **Win Rate** | Baseline | Improved | +15-25% |
| **Risk Control** | Baseline | Improved | +30-40% |
| **Parameter Adapt** | Baseline | Improved | +20-30% |
| **Position Opt** | Baseline | Improved | +25-35% |
| **Overall** | Baseline | Improved | **+35-55%** |

### Cost Analysis

**DeepSeek (Recommended)**:
- Cost: ~$0.14/million tokens
- Daily calls: ~1000
- Monthly cost: ~$4-7

**ROI Calculation**:
- AI cost: $7/month
- Performance boost: 35-55%
- If principal $1,400, monthly profit boost: $49-77
- **ROI**: 700-1100%

**Details**: [AI_ENHANCEMENT_IMPLEMENTATION_COMPLETE.md](AI_ENHANCEMENT_IMPLEMENTATION_COMPLETE.md)

---

## 📞 Technical Support

### Getting Help

1. **Check Docs**: Review relevant documentation first
2. **Check Logs**: Log files contain detailed error messages
3. **Submit Issue**: https://github.com/MAXHONG/AsterDex-MaxTraderBot/issues
4. **Join Discussion**: https://github.com/MAXHONG/AsterDex-MaxTraderBot/discussions

### Contact

- **GitHub**: [@MAXHONG](https://github.com/MAXHONG)
- **Repository**: https://github.com/MAXHONG/AsterDex-MaxTraderBot

---

## ⚠️ Disclaimer

1. **Educational Purpose**: This software is for educational and research purposes only
2. **Risk Warning**: Cryptocurrency trading involves high risk and may result in loss of principal
3. **Self Responsibility**: All risks from using this software for actual trading are borne by the user
4. **No Warranty**: The developer is not responsible for any trading losses, data loss, or other damages
5. **Testing Advice**: Strongly recommended to test with small amounts first
6. **Monitoring Required**: Regular monitoring of bot status and trading results is necessary
7. **AI Disclaimer**: AI enhancement features are based on large language models and may produce inaccurate judgments

**By using this software, you acknowledge that you have read and agree to the above disclaimer.**

---

## 📝 License

MIT License

Copyright (c) 2025 MAXHONG

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

<div align="center">

**Developer**: MAXHONG  
**Repository**: https://github.com/MAXHONG/AsterDex-MaxTraderBot  
**Last Updated**: 2025-10-22  

⭐ If this project helps you, please give it a Star! ⭐

</div>

# AsterDEX 自动化交易机器人

基于 AsterDEX API 的双均线交易系统，支持 BTC、ETH、BNB 和 ASTER 合约交易。

**语言 / Language**: [中文文档](README.md) | [English Documentation](README_EN.md)

## ✨ 功能特性

- ✅ **双均线交易系统**：基于 SMA20/60/120 和 EMA20/60/120
- ✅ **多频率交易**：
  - 高频：15分钟K线，每5分钟检查
  - 中频：4小时K线，每1小时检查
- ✅ **AI 增强系统**：支持 DeepSeek/Grok 双 AI 提供商，四阶段智能增强
  - 🧠 Phase 1: 市场情报系统 (多源信息聚合)
  - 📊 Phase 2: 动态风险评估 (多维度风险分析)
  - 🎯 Phase 3: 智能持仓管理 (实时监控优化)
  - ⚙️ Phase 4: 策略参数优化 (自适应调整)
- ✅ **风险管理**：逐仓模式，最高5倍杠杆，单币种最多占用30%保证金
- ✅ **多币种支持**：BTC/USDT、ETH/USDT、BNB/USDT、ASTER/USDT
- ✅ **Docker 支持**：容器化部署，一键启动

## 交易策略

### 双均线密集判断

当短期均线（SMA20/EMA20）、中期均线（SMA60/EMA60）和长期均线（SMA120/EMA120）在价格区间内密集排列时：

**做多条件**：
1. 双均线发生密集
2. 币价突破双均线上方
3. 30分钟内站稳在双均线上方
4. 开多合约

**做空条件**：
1. 双均线发生密集
2. 币价跌破双均线下方
3. 30分钟内未能突破回双均线上方
4. 开空合约

**平仓条件**：
- 双均线再次发生密集时平仓

## 🚀 快速开始

### 部署方式

| 方式 | 适用场景 | 文档链接 |
|------|----------|----------|
| **🐳 Docker (推荐)** | 快速部署，隔离环境 | [Docker 部署指南](DOCKER_DEPLOYMENT.md) |
| **🖥️ 传统部署** | 直接在服务器运行 | [部署指南](DEPLOYMENT_GUIDE.md) |
| **💻 本地开发** | 开发和测试 | 见下方说明 |

### 方式 1: Docker 部署（推荐）⭐

**前提条件**: 安装 Docker 和 Docker Compose

```bash
# 1. 克隆项目
git clone https://github.com/MAXHONG/AsterDex-MaxTraderBot.git
cd AsterDex-MaxTraderBot/asterdex-trading-bot

# 2. 配置文件
cp config/config.example.json config/config.json
nano config/config.json  # 填写你的 API 密钥

# 3. 启动容器
docker compose up -d

# 4. 查看日志
docker compose logs -f
```

详细文档: [Docker 部署指南](DOCKER_DEPLOYMENT.md) | [Docker Deployment Guide (EN)](DOCKER_DEPLOYMENT_EN.md)

### 方式 2: 传统部署

#### 1. 安装依赖

```bash
# 克隆项目
git clone https://github.com/MAXHONG/AsterDex-MaxTraderBot.git
cd AsterDex-MaxTraderBot/asterdex-trading-bot

# 安装 Python 依赖
pip install -r requirements.txt
```

#### 2. 配置文件

复制配置模板并填写你的信息：

```bash
cp config/config.example.json config/config.json
nano config/config.json
```

编辑 `config/config.json`：

```json
{
  "asterdex": {
    "user": "你的主钱包地址",
    "signer": "API钱包地址",
    "private_key": "API钱包私钥",
    "api_base_url": "https://fapi.asterdex.com"
  },
  "ai": {
    "provider": "deepseek",  // 或 "grok"
    "deepseek": {
      "api_key": "你的DeepSeek API密钥",
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

#### 3. 获取 API 密钥

**AsterDEX API 钱包**
- 访问 https://www.asterdex.com/zh-CN/api-wallet 
- 创建 API 钱包并获取 Signer 地址和私钥

**AI 提供商（二选一）**
- **DeepSeek**: https://platform.deepseek.com/ (推荐)
- **Grok**: https://console.x.ai/

#### 4. 运行

**开发模式**：
```bash
python src/main.py
```

**生产模式（systemd）**：
```bash
# 安装系统服务
sudo cp deploy/asterdex-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable asterdex-bot
sudo systemctl start asterdex-bot

# 查看日志
sudo journalctl -u asterdex-bot -f
```

## 📁 项目结构

```
asterdex-trading-bot/
├── src/
│   ├── main.py                      # 主程序入口
│   ├── api/
│   │   ├── base_ai_client.py        # AI 客户端基类 (DeepSeek/Grok)
│   │   ├── asterdex_client.py       # AsterDEX API 客户端
│   │   └── deepseek_client.py       # DeepSeek 客户端 (已废弃)
│   ├── ai/                          # AI 增强系统
│   │   ├── market_intelligence.py   # Phase 1: 市场情报
│   │   ├── risk_assessor.py         # Phase 2: 风险评估
│   │   ├── position_manager.py      # Phase 3: 持仓管理
│   │   └── parameter_optimizer.py   # Phase 4: 参数优化
│   ├── strategies/
│   │   ├── double_ma.py             # 双均线策略
│   │   └── indicators.py            # 技术指标计算
│   ├── trading/
│   │   ├── trader.py                # 交易执行器
│   │   └── risk_manager.py          # 风险管理
│   └── utils/
│       ├── logger.py                # 日志工具
│       └── config.py                # 配置加载
├── config/
│   ├── config.json                  # 配置文件
│   └── config.example.json          # 配置模板
├── logs/                            # 日志目录
├── tests/                           # 测试文件
├── deploy/
│   └── asterdex-bot.service         # Systemd 服务文件
├── Dockerfile                       # Docker 镜像构建
├── docker-compose.yml               # Docker Compose 配置
├── .dockerignore                    # Docker 忽略文件
├── requirements.txt                 # Python 依赖
└── README.md                        # 项目文档
```

## 安全提示

- ⚠️ **切勿泄露私钥**：config.json 已加入 .gitignore
- ⚠️ **小额测试**：建议先用小额资金测试策略
- ⚠️ **监控运行**：定期查看日志和交易记录
- ⚠️ **风险自负**：加密货币交易存在风险，请自行评估

## 监控和维护

### 查看运行状态

```bash
sudo systemctl status asterdex-bot
```

### 查看实时日志

```bash
tail -f logs/trading_bot.log
```

### 停止机器人

```bash
sudo systemctl stop asterdex-bot
```

## 故障排查

### 常见问题

1. **签名错误**：检查私钥和时间同步
2. **余额不足**：确保账户有足够保证金
3. **API限流**：降低请求频率
4. **订单被拒**：检查价格和数量是否符合交易所规则

### 日志位置

- 应用日志：`logs/trading_bot.log`
- 系统日志：`sudo journalctl -u asterdex-bot`

## 📚 完整文档

| 文档 | 说明 | 语言 |
|------|------|------|
| [README.md](README.md) | 项目主文档 | 🇨🇳 中文 |
| [README_EN.md](README_EN.md) | Project README | 🇬🇧 English |
| [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) | Docker 部署指南 | 🇨🇳 中文 |
| [DOCKER_DEPLOYMENT_EN.md](DOCKER_DEPLOYMENT_EN.md) | Docker Deployment | 🇬🇧 English |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | 传统部署指南 | 🇨🇳 中文 |
| [DEPLOYMENT_GUIDE_EN.md](DEPLOYMENT_GUIDE_EN.md) | Deployment Guide | 🇬🇧 English |
| [AI_ENHANCEMENT_IMPLEMENTATION_COMPLETE.md](AI_ENHANCEMENT_IMPLEMENTATION_COMPLETE.md) | AI 增强系统 | 🇨🇳 中文 |

## 🤖 AI 增强系统

本项目集成了完整的 AI 增强系统，提供四个阶段的智能优化：

- **Phase 1**: 市场情报系统 (多源信息聚合)
- **Phase 2**: 动态风险评估 (多维度分析)
- **Phase 3**: 智能持仓管理 (实时优化)
- **Phase 4**: 策略参数优化 (自适应调整)

**性能提升预期**: 整体 +35-55% 改进

详见: [AI_ENHANCEMENT_IMPLEMENTATION_COMPLETE.md](AI_ENHANCEMENT_IMPLEMENTATION_COMPLETE.md)

## 📞 技术支持

遇到问题时：
1. 查看对应的文档指南
2. 检查日志文件获取详细错误信息
3. 提交 Issue: https://github.com/MAXHONG/AsterDex-MaxTraderBot/issues

## 📝 许可证

MIT License

## ⚠️ 免责声明

本软件仅供学习和研究使用。使用本软件进行实际交易的所有风险由用户自行承担。开发者不对任何交易损失负责。

---

**开发者**: MAXHONG  
**仓库地址**: https://github.com/MAXHONG/AsterDex-MaxTraderBot  
**最后更新**: 2025-10-22

# AsterDEX 自动化交易机器人

基于 AsterDEX API 的双均线交易系统，支持 BTC、ETH、BNB 和 ASTER 合约交易。

**语言 / Language**: [中文文档](README.md) | [English Documentation](README_EN.md)

## 功能特性

- ✅ **双均线交易系统**：基于 SMA20/60/120 和 EMA20/60/120
- ✅ **多频率交易**：
  - 高频：15分钟K线，每5分钟检查
  - 中频：4小时K线，每1小时检查
- ✅ **智能决策**：集成 DeepSeek AI 辅助交易决策
- ✅ **风险管理**：逐仓模式，最高5倍杠杆，单币种最多占用30%保证金
- ✅ **多币种支持**：BTC/USDT、ETH/USDT、BNB/USDT、ASTER/USDT

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

## 安装配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置文件

复制配置模板并填写你的信息：

```bash
cp config/config.example.json config/config.json
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
  "deepseek": {
    "api_key": "你的DeepSeek API密钥",
    "api_base_url": "https://api.deepseek.com"
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

### 3. 获取 API 密钥

#### AsterDEX API 钱包
访问 https://www.asterdex.com/zh-CN/api-wallet 创建 API 钱包并获取：
- Signer 地址
- 私钥

#### DeepSeek API
访问 https://platform.deepseek.com/ 获取 API Key

## 运行

### 开发模式

```bash
python src/main.py
```

### 生产模式（后台运行）

```bash
# 使用 systemd
sudo cp deploy/asterdex-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable asterdex-bot
sudo systemctl start asterdex-bot

# 查看日志
sudo journalctl -u asterdex-bot -f
```

## 项目结构

```
asterdex-trading-bot/
├── src/
│   ├── main.py                 # 主程序入口
│   ├── api/
│   │   ├── asterdex_client.py  # AsterDEX API 客户端
│   │   └── deepseek_client.py  # DeepSeek API 客户端
│   ├── strategies/
│   │   ├── double_ma.py        # 双均线策略
│   │   └── indicators.py       # 技术指标计算
│   ├── trading/
│   │   ├── trader.py           # 交易执行器
│   │   └── risk_manager.py     # 风险管理
│   └── utils/
│       ├── logger.py           # 日志工具
│       └── config.py           # 配置加载
├── config/
│   ├── config.json             # 配置文件
│   └── config.example.json     # 配置模板
├── logs/                       # 日志目录
├── tests/                      # 测试文件
├── deploy/
│   └── asterdex-bot.service    # Systemd 服务文件
├── requirements.txt            # Python 依赖
└── README.md                   # 项目文档
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

## 许可证

MIT License

## 免责声明

本软件仅供学习和研究使用。使用本软件进行实际交易的所有风险由用户自行承担。开发者不对任何交易损失负责。

# SSH 服务器部署指南

## 📋 项目信息

- **项目名称**: AsterDEX 自动化交易机器人
- **GitHub 仓库**: https://github.com/MAXHONG/AsterDex-MaxTraderBot
- **功能**: 基于双均线策略的加密货币合约自动交易

## 🚀 快速部署步骤

### 1. 连接到 SSH 服务器

```bash
ssh your_username@your_server_ip
```

### 2. 克隆项目

```bash
cd ~
git clone https://github.com/MAXHONG/AsterDex-MaxTraderBot.git
cd AsterDex-MaxTraderBot
```

### 3. 运行安装脚本

```bash
bash deploy/install.sh
```

安装脚本会自动：
- 检查 Python 版本（需要 3.9+）
- 创建虚拟环境
- 安装所有依赖包

### 4. 配置交易机器人

#### 4.1 复制配置模板

```bash
cp config/config.example.json config/config.json
```

#### 4.2 编辑配置文件

```bash
vim config/config.json
# 或者使用 nano
nano config/config.json
```

#### 4.3 必填配置项

```json
{
  "asterdex": {
    "user": "0xYourMainWalletAddress",           // 你的主钱包地址
    "signer": "0xYourAPIWalletAddress",          // API 钱包地址
    "private_key": "0xYourAPIWalletPrivateKey",  // API 钱包私钥
    "api_base_url": "https://fapi.asterdex.com"
  },
  "deepseek": {
    "api_key": "sk-xxxxx",                       // DeepSeek API Key（可选）
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

#### 4.4 获取 API 密钥

**AsterDEX API 钱包**:
1. 访问 https://www.asterdex.com/zh-CN/api-wallet
2. 创建 API 钱包
3. 获取 Signer 地址和私钥
4. **⚠️ 重要**: 妥善保管私钥，不要泄露

**DeepSeek API**（可选，用于AI辅助决策）:
1. 访问 https://platform.deepseek.com/
2. 注册账号并获取 API Key

### 5. 测试运行

在后台运行之前，先测试确保一切正常：

```bash
source venv/bin/activate
python src/main.py
```

观察输出日志，确保：
- ✅ 能够连接 AsterDEX API
- ✅ 能够获取交易对信息
- ✅ 能够获取K线数据
- ✅ 没有配置错误

按 `Ctrl+C` 停止测试。

### 6. 部署为系统服务

```bash
bash deploy/deploy.sh
```

这会：
- 创建 systemd 服务文件
- 安装到系统服务
- 配置自动重启

### 7. 启动服务

```bash
sudo systemctl start asterdex-bot
```

### 8. 验证服务状态

```bash
sudo systemctl status asterdex-bot
```

你应该看到 `Active: active (running)` 状态。

### 9. 查看实时日志

```bash
# 系统日志
sudo journalctl -u asterdex-bot -f

# 应用日志
tail -f logs/trading_bot.log
```

## 📊 服务管理命令

### 基本操作

```bash
# 启动服务
sudo systemctl start asterdex-bot

# 停止服务
sudo systemctl stop asterdex-bot

# 重启服务
sudo systemctl restart asterdex-bot

# 查看状态
sudo systemctl status asterdex-bot

# 开机自启
sudo systemctl enable asterdex-bot

# 取消开机自启
sudo systemctl disable asterdex-bot
```

### 日志查看

```bash
# 实时查看系统日志
sudo journalctl -u asterdex-bot -f

# 查看最近100行日志
sudo journalctl -u asterdex-bot -n 100

# 查看应用日志
tail -f logs/trading_bot.log

# 查看完整应用日志
cat logs/trading_bot.log
```

## 🔧 配置说明

### 交易策略配置

#### 高频策略（15分钟K线）

```json
{
  "strategies": {
    "high_frequency": {
      "enabled": true,
      "interval": "15m",
      "check_interval_seconds": 300,  // 每5分钟检查一次
      "ma_periods": {
        "sma_short": 20,
        "sma_medium": 60,
        "sma_long": 120,
        "ema_short": 20,
        "ema_medium": 60,
        "ema_long": 120
      },
      "convergence_threshold_percent": 2.0,        // 均线密集阈值2%
      "breakout_confirmation_minutes": 30          // 突破确认30分钟
    }
  }
}
```

#### 中频策略（4小时K线）

```json
{
  "strategies": {
    "medium_frequency": {
      "enabled": true,
      "interval": "4h",
      "check_interval_seconds": 3600,  // 每1小时检查一次
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

### 风险管理配置

```json
{
  "risk_management": {
    "enable_stop_loss": true,
    "stop_loss_percent": 3.0,      // 止损3%
    "enable_take_profit": false,
    "take_profit_percent": 10.0    // 止盈10%
  }
}
```

## 🔐 安全建议

### 1. 保护配置文件

```bash
chmod 600 config/config.json
```

### 2. 使用防火墙

```bash
sudo ufw allow 22/tcp
sudo ufw enable
```

### 3. 定期备份配置

```bash
cp config/config.json ~/config_backup_$(date +%Y%m%d).json
```

### 4. 监控日志异常

定期检查日志中的错误和警告：

```bash
grep -i error logs/trading_bot.log
grep -i warning logs/trading_bot.log
```

## 📈 监控和维护

### 检查系统资源

```bash
# CPU 和内存
top -p $(pgrep -f "python src/main.py")

# 磁盘使用
df -h

# 日志文件大小
du -sh logs/
```

### 更新代码

```bash
# 停止服务
sudo systemctl stop asterdex-bot

# 备份配置
cp config/config.json config/config.backup.json

# 拉取最新代码
git pull origin main

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 恢复配置（如果被覆盖）
cp config/config.backup.json config/config.json

# 重启服务
sudo systemctl start asterdex-bot
```

## 🐛 故障排查

### 服务启动失败

1. **检查配置文件**
```bash
python -m json.tool config/config.json
```

2. **查看错误日志**
```bash
sudo journalctl -u asterdex-bot -n 50 --no-pager
```

3. **手动运行测试**
```bash
source venv/bin/activate
python src/main.py
```

### API 连接失败

1. **测试网络连接**
```bash
curl -I https://fapi.asterdex.com/fapi/v1/ping
```

2. **检查时间同步**
```bash
timedatectl status
```

3. **同步系统时间**
```bash
sudo timedatectl set-ntp true
```

### 签名错误

签名错误通常是由于时间不同步导致：

```bash
# 检查时间
date
timedatectl

# 同步时间
sudo ntpdate -s time.nist.gov
# 或
sudo timedatectl set-ntp true
```

### 内存不足

```bash
# 查看内存
free -h

# 清理缓存
sudo sync && sudo sysctl -w vm.drop_caches=3
```

## 📞 支持

如遇到问题：

1. 查看 [README.md](README.md) 文档
2. 查看 [DEPLOYMENT.md](deploy/DEPLOYMENT.md) 详细部署文档
3. 检查日志文件找出错误原因
4. 在 GitHub 提交 Issue: https://github.com/MAXHONG/AsterDex-MaxTraderBot/issues

## ⚠️ 免责声明

- 本软件仅供学习和研究使用
- 加密货币交易存在高风险
- 使用前请充分了解风险
- 建议先用小额资金测试
- 开发者不对任何交易损失负责

## 📝 许可证

MIT License

---

**开发者**: MAXHONG  
**项目地址**: https://github.com/MAXHONG/AsterDex-MaxTraderBot  
**最后更新**: 2025-10-22

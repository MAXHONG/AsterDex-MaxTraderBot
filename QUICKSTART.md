# 快速开始指南

本指南帮助你在 5 分钟内启动 AsterDEX 自动化交易机器人。

## 📋 前置要求

- Python 3.9+
- pip
- git
- AsterDEX 账户和 API 钱包
- （可选）DeepSeek API 密钥

## 🚀 快速部署（3步）

### 步骤 1: 克隆并安装

```bash
# 克隆项目
git clone <your-repo-url> asterdex-trading-bot
cd asterdex-trading-bot

# 一键安装
bash deploy/install.sh
```

### 步骤 2: 配置

```bash
# 复制配置模板
cp config/config.example.json config/config.json

# 编辑配置（填写你的钱包地址和私钥）
vim config/config.json
```

**最小配置示例：**

```json
{
  "asterdex": {
    "user": "0xYourMainWalletAddress",
    "signer": "0xYourAPIWalletAddress",
    "private_key": "0xYourAPIWalletPrivateKey"
  },
  "deepseek": {
    "api_key": ""
  },
  "trading": {
    "symbols": ["BTCUSDT"],
    "max_leverage": 3,
    "max_position_percent": 20
  },
  "strategies": {
    "high_frequency": {
      "enabled": true
    }
  }
}
```

### 步骤 3: 运行

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动机器人
python src/main.py
```

## 🔧 获取 API 密钥

### AsterDEX API 钱包

1. 访问 https://www.asterdex.com/zh-CN/api-wallet
2. 连接你的主钱包
3. 创建 API 钱包
4. 复制 `Signer 地址` 和 `私钥`
5. 填入 `config.json`

### DeepSeek API（可选）

1. 访问 https://platform.deepseek.com/
2. 注册并登录
3. 创建 API Key
4. 填入 `config.json` 的 `deepseek.api_key`

## 📊 测试配置

测试模块导入：

```bash
python test_import.py
```

测试 API 连接：

```bash
python -c "
import sys
sys.path.insert(0, 'src')
from api import AsterDexClient
from utils import get_config

config = get_config()
client = AsterDexClient(
    user=config.asterdex['user'],
    signer=config.asterdex['signer'],
    private_key=config.asterdex['private_key']
)
print('Server time:', client.get_server_time())
print('✅ API 连接成功')
"
```

## 🎯 推荐配置

### 新手（保守）

```json
{
  "trading": {
    "symbols": ["BTCUSDT"],
    "max_leverage": 2,
    "max_position_percent": 10
  },
  "strategies": {
    "medium_frequency": {
      "enabled": true
    }
  }
}
```

### 进阶（平衡）

```json
{
  "trading": {
    "symbols": ["BTCUSDT", "ETHUSDT"],
    "max_leverage": 3,
    "max_position_percent": 20
  },
  "strategies": {
    "high_frequency": {
      "enabled": true
    },
    "medium_frequency": {
      "enabled": true
    }
  }
}
```

### 高级（激进）

```json
{
  "trading": {
    "symbols": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ASTERUSDT"],
    "max_leverage": 5,
    "max_position_percent": 30
  },
  "strategies": {
    "high_frequency": {
      "enabled": true
    },
    "medium_frequency": {
      "enabled": true
    }
  }
}
```

## 🔐 安全提示

1. **保护私钥**：
   ```bash
   chmod 600 config/config.json
   ```

2. **使用小额测试**：
   - 建议先用小额资金测试
   - 观察运行 24-48 小时

3. **设置告警**：
   - 定期检查日志
   - 监控账户余额

## 📱 监控机器人

### 查看日志

```bash
# 实时日志
tail -f logs/trading_bot.log

# 查看最近的信号
tail -n 50 logs/trading_bot.log | grep "信号"

# 查看交易记录
tail -n 50 logs/trading_bot.log | grep "开仓\|平仓"
```

### 停止机器人

按 `Ctrl+C` 或：

```bash
# 如果是后台运行
pkill -f "python src/main.py"
```

## 🐛 常见问题

### Q: 签名错误？

**A:** 检查时间同步：
```bash
timedatectl status
sudo timedatectl set-ntp true
```

### Q: 模块导入错误？

**A:** 确保虚拟环境激活：
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Q: API 连接失败？

**A:** 检查网络和 API 密钥：
```bash
curl -I https://fapi.asterdex.com
# 检查配置文件中的密钥是否正确
```

### Q: 没有生成交易信号？

**A:** 这是正常的！双均线策略需要等待：
- 均线密集
- 价格突破
- 站稳确认

可能需要等待几小时到几天才有信号。

## 📚 下一步

- 阅读 [README.md](README.md) 了解详细功能
- 阅读 [deploy/DEPLOYMENT.md](deploy/DEPLOYMENT.md) 了解生产部署
- 查看策略配置调整交易参数

## 💡 建议

1. **从单个币种开始**
2. **使用较低杠杆（2-3x）**
3. **监控至少 24 小时**
4. **定期检查日志和余额**
5. **不要投入超过承受能力的资金**

## ⚠️ 免责声明

- 加密货币交易存在高风险
- 过去的表现不代表未来收益
- 请自行评估风险，谨慎投资
- 开发者不对任何交易损失负责

## 🆘 获取帮助

遇到问题？

1. 查看日志文件
2. 阅读完整文档
3. 提交 GitHub Issue
4. 检查配置是否正确

---

**祝交易顺利！** 🚀

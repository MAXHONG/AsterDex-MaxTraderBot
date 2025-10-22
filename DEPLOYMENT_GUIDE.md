# 🚀 AsterDEX 交易机器人 - SSH 服务器部署指南

本指南将帮助你在远程 SSH 服务器上部署和运行 AsterDEX 自动化交易机器人。

## 📋 部署前检查清单

在开始部署前，请确保你已准备好：

- ✅ SSH 服务器访问权限（需要 sudo 权限）
- ✅ Python 3.9+ 已安装
- ✅ Git 已安装
- ✅ AsterDEX 主钱包地址
- ✅ AsterDEX API 钱包地址和私钥
- ✅ （可选）DeepSeek API 密钥

## 🔐 获取 API 密钥

### 1. AsterDEX API 钱包

访问：https://www.asterdex.com/zh-CN/api-wallet

步骤：
1. 连接你的主钱包（MetaMask/WalletConnect）
2. 点击"创建 API 钱包"
3. 复制并保存：
   - **User**: 主钱包地址（0x...）
   - **Signer**: API 钱包地址（0x...）
   - **Private Key**: API 钱包私钥（0x...）

⚠️ **重要**: 私钥只显示一次，请妥善保存！

### 2. DeepSeek API（可选，用于 AI 辅助决策）

访问：https://platform.deepseek.com/

步骤：
1. 注册并登录
2. 进入 API Keys 页面
3. 创建新的 API Key
4. 复制保存（格式：sk-xxxxxx）

## 📥 步骤 1: 连接到 SSH 服务器

```bash
# 连接到服务器
ssh username@your-server-ip

# 或使用密钥
ssh -i ~/.ssh/your_key.pem username@your-server-ip
```

## 📦 步骤 2: 克隆项目

```bash
# 方式 1: 从 GitHub 克隆（推荐）
cd ~
git clone https://github.com/your-username/asterdex-trading-bot.git
cd asterdex-trading-bot

# 方式 2: 上传本地代码
# 在本地执行：
# scp -r asterdex-trading-bot username@your-server-ip:~/
```

## 🔧 步骤 3: 运行安装脚本

```bash
# 执行一键安装
bash deploy/install.sh
```

安装脚本会自动：
- ✅ 检查 Python 版本
- ✅ 创建虚拟环境
- ✅ 安装所有依赖包

预计耗时：2-5 分钟

## ⚙️ 步骤 4: 配置机器人

### 4.1 复制配置模板

```bash
cp config/config.example.json config/config.json
```

### 4.2 编辑配置文件

```bash
# 使用 vim
vim config/config.json

# 或使用 nano（更友好）
nano config/config.json
```

### 4.3 最小配置（必需）

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
    },
    "medium_frequency": {
      "enabled": false
    }
  }
}
```

**编辑提示：**
- vim: 按 `i` 进入编辑模式，编辑完成后按 `ESC`，输入 `:wq` 保存退出
- nano: 编辑完成后按 `Ctrl+X`，输入 `Y` 确认，按 `Enter` 保存

### 4.4 保护配置文件

```bash
# 设置文件权限为仅所有者可读写
chmod 600 config/config.json
```

## 🧪 步骤 5: 测试运行

### 5.1 测试模块导入

```bash
python test_import.py
```

预期输出：
```
测试导入模块...
✅ utils 模块导入成功
✅ api 模块导入成功
✅ strategies 模块导入成功
✅ trading 模块导入成功

所有模块导入成功！✅
```

### 5.2 测试 API 连接

```bash
source venv/bin/activate
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

### 5.3 短暂运行测试

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动机器人（前台运行）
python src/main.py
```

观察输出：
- 机器人启动日志
- 策略初始化信息
- K线数据获取
- 交易信号分析

**测试时间**：运行 1-2 分钟后按 `Ctrl+C` 停止

## 🎯 步骤 6: 部署为系统服务（推荐）

### 6.1 运行部署脚本

```bash
# 确保在项目根目录
cd ~/asterdex-trading-bot

# 执行部署脚本
bash deploy/deploy.sh
```

脚本会：
1. 创建 systemd 服务配置
2. 安装服务到系统（需要输入 sudo 密码）
3. 配置自动重启

### 6.2 启动服务

```bash
# 启动服务
sudo systemctl start asterdex-bot

# 查看状态
sudo systemctl status asterdex-bot
```

预期状态：`active (running)`

### 6.3 启用开机自启动

```bash
sudo systemctl enable asterdex-bot
```

## 📊 步骤 7: 监控运行

### 7.1 实时查看日志

```bash
# 方式 1: 系统日志
sudo journalctl -u asterdex-bot -f

# 方式 2: 应用日志
tail -f logs/trading_bot.log
```

### 7.2 检查服务状态

```bash
# 查看服务状态
sudo systemctl status asterdex-bot

# 查看最近日志
sudo journalctl -u asterdex-bot -n 50 --no-pager
```

### 7.3 查看交易信号

```bash
# 查看最近的交易信号
tail -n 100 logs/trading_bot.log | grep "信号"

# 查看开仓/平仓记录
tail -n 100 logs/trading_bot.log | grep "开仓\|平仓"
```

## 🔄 服务管理命令

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

# 禁用自启
sudo systemctl disable asterdex-bot
```

## 🛠️ 故障排查

### 问题 1: 服务启动失败

**排查步骤：**

```bash
# 1. 查看详细错误
sudo journalctl -u asterdex-bot -n 50 --no-pager

# 2. 检查配置文件
python -m json.tool config/config.json

# 3. 检查文件权限
ls -la config/config.json

# 4. 手动运行测试
source venv/bin/activate
python src/main.py
```

### 问题 2: API 签名错误

**原因**: 服务器时间不同步

**解决方案：**

```bash
# 检查时间
timedatectl status

# 同步时间
sudo timedatectl set-ntp true

# 重启服务
sudo systemctl restart asterdex-bot
```

### 问题 3: 内存不足

**检查内存：**

```bash
free -h
```

**解决方案：**
- 减少监控的币种数量
- 调整日志级别为 WARNING
- 考虑升级服务器配置

### 问题 4: 没有交易信号

**这是正常的！** 双均线策略需要等待合适时机：

- 均线必须密集
- 价格必须突破
- 需要确认站稳

可能需要等待数小时至数天才有信号。

## 🔒 安全最佳实践

### 1. 防火墙设置

```bash
# 安装 ufw
sudo apt install ufw

# 允许 SSH
sudo ufw allow 22/tcp

# 启用防火墙
sudo ufw enable
```

### 2. 定期备份配置

```bash
# 创建备份脚本
cat > ~/backup_config.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d)
cp ~/asterdex-trading-bot/config/config.json ~/config_backup_${DATE}.json
echo "配置已备份到: ~/config_backup_${DATE}.json"
EOF

chmod +x ~/backup_config.sh

# 运行备份
~/backup_config.sh
```

### 3. 定期更新

```bash
# 停止服务
sudo systemctl stop asterdex-bot

# 拉取最新代码
cd ~/asterdex-trading-bot
git pull

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 重启服务
sudo systemctl start asterdex-bot
```

## 📈 性能优化建议

### 1. 调整检查频率

编辑 `config/config.json`:

```json
{
  "strategies": {
    "high_frequency": {
      "check_interval_seconds": 600
    }
  }
}
```

### 2. 调整日志级别

```json
{
  "logging": {
    "level": "WARNING"
  }
}
```

### 3. 减少币种数量

```json
{
  "trading": {
    "symbols": ["BTCUSDT", "ETHUSDT"]
  }
}
```

## 📞 获取支持

如遇问题：

1. **查看日志**: `tail -f logs/trading_bot.log`
2. **检查状态**: `sudo systemctl status asterdex-bot`
3. **阅读文档**: 
   - README.md
   - QUICKSTART.md
   - PROJECT_SUMMARY.md
4. **提交 Issue**: 到 GitHub 仓库提交问题

## ✅ 部署验证清单

部署完成后，请确认：

- [ ] 服务状态为 `active (running)`
- [ ] 日志正常输出（无错误）
- [ ] 能够获取 K线数据
- [ ] 策略正常运行
- [ ] 账户余额可查询
- [ ] 开机自启已启用

## 🎉 部署完成

恭喜！你已成功部署 AsterDEX 自动化交易机器人。

**下一步：**

1. 监控运行状态（前 24-48 小时）
2. 观察交易信号
3. 根据需要调整参数
4. 定期检查日志和余额

**祝交易顺利！** 🚀

---

**提示**: 建议在真实交易前，先用小额资金测试至少 1-2 周。

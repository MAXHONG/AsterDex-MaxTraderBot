# 部署指南

本文档介绍如何在 SSH 服务器上部署 AsterDEX 交易机器人。

## 前置要求

- Python 3.9 或更高版本
- pip
- git
- sudo 权限（用于安装系统服务）

## 快速部署

### 1. 克隆项目

```bash
git clone <your-repo-url> asterdex-trading-bot
cd asterdex-trading-bot
```

### 2. 运行安装脚本

```bash
bash deploy/install.sh
```

这将：
- 检查 Python 版本
- 创建虚拟环境
- 安装所有依赖

### 3. 配置机器人

复制配置模板：

```bash
cp config/config.example.json config/config.json
```

编辑配置文件：

```bash
vim config/config.json
# 或
nano config/config.json
```

必填配置项：

```json
{
  "asterdex": {
    "user": "你的主钱包地址（0x...）",
    "signer": "API 钱包地址（0x...）",
    "private_key": "API 钱包私钥（0x...）"
  },
  "deepseek": {
    "api_key": "DeepSeek API 密钥（可选）"
  },
  "trading": {
    "symbols": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ASTERUSDT"],
    "max_leverage": 5,
    "max_position_percent": 30
  }
}
```

### 4. 测试运行

```bash
source venv/bin/activate
python src/main.py
```

按 `Ctrl+C` 停止。

### 5. 部署为系统服务

```bash
bash deploy/deploy.sh
```

这将创建并安装 systemd 服务。

### 6. 启动服务

```bash
sudo systemctl start asterdex-bot
```

## 服务管理

### 启动服务

```bash
sudo systemctl start asterdex-bot
```

### 停止服务

```bash
sudo systemctl stop asterdex-bot
```

### 重启服务

```bash
sudo systemctl restart asterdex-bot
```

### 查看状态

```bash
sudo systemctl status asterdex-bot
```

### 查看日志

实时查看日志：

```bash
sudo journalctl -u asterdex-bot -f
```

查看最近100行日志：

```bash
sudo journalctl -u asterdex-bot -n 100
```

查看应用日志文件：

```bash
tail -f logs/trading_bot.log
```

### 开机自启动

启用开机自启：

```bash
sudo systemctl enable asterdex-bot
```

禁用开机自启：

```bash
sudo systemctl disable asterdex-bot
```

## 手动部署（不使用脚本）

### 1. 创建虚拟环境

```bash
python3 -m venv venv
```

### 2. 激活虚拟环境

```bash
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. 配置服务

编辑 `deploy/asterdex-bot.service`，替换以下占位符：

- `your_username` → 你的用户名
- `/path/to/asterdex-trading-bot` → 项目绝对路径
- `/path/to/venv` → 虚拟环境路径

### 5. 安装服务

```bash
sudo cp deploy/asterdex-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
```

## 监控和维护

### 监控系统资源

```bash
# CPU 和内存使用
top -p $(pgrep -f "python src/main.py")

# 或使用 htop
htop -p $(pgrep -f "python src/main.py")
```

### 日志轮转

日志文件会自动轮转（最大 10MB，保留 5 个备份）。

查看日志文件：

```bash
ls -lh logs/
```

### 更新代码

```bash
# 停止服务
sudo systemctl stop asterdex-bot

# 拉取最新代码
git pull

# 更新依赖（如果有变化）
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo systemctl start asterdex-bot
```

### 备份配置

定期备份配置文件：

```bash
cp config/config.json config/config.backup.$(date +%Y%m%d).json
```

## 故障排查

### 服务无法启动

1. 检查配置文件是否存在：
   ```bash
   ls -l config/config.json
   ```

2. 检查配置文件格式：
   ```bash
   python -m json.tool config/config.json
   ```

3. 查看详细错误日志：
   ```bash
   sudo journalctl -u asterdex-bot -n 50 --no-pager
   ```

### API 连接失败

1. 检查网络连接：
   ```bash
   curl -I https://fapi.asterdex.com
   ```

2. 验证 API 密钥是否正确

3. 检查防火墙设置

### 签名错误

1. 检查系统时间是否同步：
   ```bash
   timedatectl status
   ```

2. 如需同步时间：
   ```bash
   sudo timedatectl set-ntp true
   ```

### 内存不足

1. 查看内存使用：
   ```bash
   free -h
   ```

2. 如需清理内存：
   ```bash
   sudo sync && sudo sysctl -w vm.drop_caches=3
   ```

## 安全建议

1. **保护私钥**：
   - 确保 `config/config.json` 权限为 600
   ```bash
   chmod 600 config/config.json
   ```

2. **使用防火墙**：
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw enable
   ```

3. **定期更新**：
   - 定期更新系统和依赖包
   ```bash
   sudo apt update && sudo apt upgrade
   pip list --outdated
   ```

4. **监控日志**：
   - 定期检查异常日志
   - 设置日志告警

## 性能优化

1. **调整检查频率**：
   - 在 `config/config.json` 中调整 `check_interval_seconds`

2. **减少交易对数量**：
   - 根据服务器性能选择合适数量的交易对

3. **使用日志级别**：
   - 生产环境使用 INFO 或 WARNING 级别
   ```json
   {
     "logging": {
       "level": "WARNING"
     }
   }
   ```

## 卸载

### 停止并删除服务

```bash
sudo systemctl stop asterdex-bot
sudo systemctl disable asterdex-bot
sudo rm /etc/systemd/system/asterdex-bot.service
sudo systemctl daemon-reload
```

### 删除项目文件

```bash
cd ..
rm -rf asterdex-trading-bot
```

## 支持

如遇问题，请：

1. 查看日志文件
2. 检查配置是否正确
3. 参考 README.md 文档
4. 提交 Issue 到 GitHub

## 许可证

MIT License

# AsterDEX 交易机器人操作指南

完整的启动、暂停、结束操作说明

[中文文档](OPERATIONS_GUIDE.md) | [English Documentation](OPERATIONS_GUIDE_EN.md)

---

## 📋 目录

- [Docker 部署操作](#docker-部署操作)
- [传统部署操作](#传统部署操作)
- [快捷命令速查](#快捷命令速查)
- [常见操作场景](#常见操作场景)
- [故障恢复](#故障恢复)

---

## 🐳 Docker 部署操作

### 1️⃣ 开启（启动）机器人

#### 首次启动

```bash
# 1. 进入项目目录
cd /home/user/webapp/asterdex-trading-bot

# 2. 确保配置文件已准备好
ls -la config/config.json

# 3. 启动容器（后台运行）
docker compose up -d

# 4. 查看启动日志
docker compose logs -f
```

**输出示例**：
```
[+] Running 1/1
 ✔ Container asterdex-trading-bot  Started
```

#### 再次启动（已有容器）

```bash
# 方法 1: 启动已停止的容器
docker compose start

# 方法 2: 如果容器被删除，重新创建并启动
docker compose up -d
```

### 2️⃣ 暂停机器人

暂停意味着**停止交易但保留所有数据和配置**。

```bash
# 停止容器（保留容器，可随时重启）
docker compose stop

# 验证已停止
docker compose ps
```

**输出示例**：
```
NAME                    STATUS
asterdex-trading-bot    Exited (0)
```

**注意**：
- ✅ 配置文件保留
- ✅ 日志文件保留
- ✅ 容器保留（下次启动更快）
- ⚠️ 交易策略停止执行
- ⚠️ 不会平仓（需要手动平仓）

### 3️⃣ 结束（完全删除）机器人

完全删除意味着**删除容器和所有运行数据**。

#### 方法 A: 仅删除容器（保留日志和配置）

```bash
# 停止并删除容器
docker compose down

# 验证已删除
docker compose ps -a
```

#### 方法 B: 完全清理（包括镜像）

```bash
# 停止并删除容器、网络、镜像
docker compose down --rmi all

# 清理未使用的 Docker 资源
docker system prune -a
```

#### 方法 C: 彻底清理（包括日志和配置）

```bash
# 1. 停止并删除容器
docker compose down --rmi all

# 2. 删除日志（可选）
rm -rf logs/*

# 3. 删除配置（危险！确保已备份）
# rm config/config.json
```

**⚠️ 警告**：
- 删除容器会丢失容器内的临时数据
- 删除镜像需要重新构建（耗时）
- 删除配置文件需要重新配置

---

## 🖥️ 传统部署操作

### 使用 Systemd（推荐）

#### 1️⃣ 开启机器人

```bash
# 启动服务
sudo systemctl start asterdex-bot

# 验证状态
sudo systemctl status asterdex-bot

# 查看实时日志
sudo journalctl -u asterdex-bot -f
```

**输出示例**：
```
● asterdex-bot.service - AsterDEX Trading Bot
   Loaded: loaded (/etc/systemd/system/asterdex-bot.service; enabled)
   Active: active (running) since Wed 2025-10-22 10:30:00 UTC; 5s ago
```

#### 2️⃣ 暂停机器人

```bash
# 停止服务
sudo systemctl stop asterdex-bot

# 验证已停止
sudo systemctl status asterdex-bot
```

**输出示例**：
```
● asterdex-bot.service - AsterDEX Trading Bot
   Active: inactive (dead) since Wed 2025-10-22 10:35:00 UTC
```

#### 3️⃣ 结束机器人

```bash
# 停止服务
sudo systemctl stop asterdex-bot

# 禁用开机自启
sudo systemctl disable asterdex-bot

# 删除服务文件（可选）
sudo rm /etc/systemd/system/asterdex-bot.service
sudo systemctl daemon-reload
```

---

### 使用 nohup（简单方式）

#### 1️⃣ 开启机器人

```bash
# 进入项目目录
cd /home/user/webapp/asterdex-trading-bot

# 激活虚拟环境
source venv/bin/activate

# 后台运行
nohup python src/main.py > logs/bot.log 2>&1 &

# 记录进程 ID
echo $! > bot.pid

# 查看日志
tail -f logs/bot.log
```

#### 2️⃣ 暂停机器人

```bash
# 查找进程 ID
ps aux | grep "python src/main.py"

# 方法 1: 使用保存的 PID
kill $(cat bot.pid)

# 方法 2: 手动杀进程
kill <PID>

# 验证已停止
ps aux | grep "python src/main.py"
```

#### 3️⃣ 结束机器人

```bash
# 强制杀死进程
kill -9 $(cat bot.pid)

# 或手动查找并杀死
pkill -f "python src/main.py"

# 清理 PID 文件
rm bot.pid
```

---

### 直接运行（开发模式）

#### 1️⃣ 开启机器人

```bash
# 进入项目目录
cd /home/user/webapp/asterdex-trading-bot

# 激活虚拟环境
source venv/bin/activate

# 前台运行（看到实时输出）
python src/main.py
```

#### 2️⃣ 暂停/结束机器人

```bash
# 按 Ctrl + C 停止
# 机器人会优雅地关闭
```

---

## ⚡ 快捷命令速查

### Docker 部署

| 操作 | 命令 | 说明 |
|------|------|------|
| **启动** | `docker compose up -d` | 后台启动容器 |
| **启动（查看日志）** | `docker compose up` | 前台启动，显示日志 |
| **暂停** | `docker compose stop` | 停止容器，保留数据 |
| **恢复** | `docker compose start` | 重启已停止的容器 |
| **重启** | `docker compose restart` | 重启容器 |
| **删除** | `docker compose down` | 删除容器，保留镜像 |
| **完全删除** | `docker compose down --rmi all` | 删除容器和镜像 |
| **查看状态** | `docker compose ps` | 查看容器状态 |
| **查看日志** | `docker compose logs -f` | 实时查看日志 |
| **进入容器** | `docker compose exec asterdex-bot bash` | 进入容器调试 |

### Systemd 服务

| 操作 | 命令 | 说明 |
|------|------|------|
| **启动** | `sudo systemctl start asterdex-bot` | 启动服务 |
| **暂停** | `sudo systemctl stop asterdex-bot` | 停止服务 |
| **重启** | `sudo systemctl restart asterdex-bot` | 重启服务 |
| **状态** | `sudo systemctl status asterdex-bot` | 查看状态 |
| **开机自启** | `sudo systemctl enable asterdex-bot` | 启用开机自启 |
| **禁用自启** | `sudo systemctl disable asterdex-bot` | 禁用开机自启 |
| **查看日志** | `sudo journalctl -u asterdex-bot -f` | 实时查看日志 |
| **最近日志** | `sudo journalctl -u asterdex-bot -n 100` | 查看最近100行 |

### 进程管理（nohup）

| 操作 | 命令 | 说明 |
|------|------|------|
| **启动** | `nohup python src/main.py > logs/bot.log 2>&1 &` | 后台启动 |
| **查找进程** | `ps aux \| grep "python src/main.py"` | 查找进程 ID |
| **停止** | `kill $(cat bot.pid)` | 优雅停止 |
| **强制停止** | `kill -9 $(cat bot.pid)` | 强制停止 |
| **查看日志** | `tail -f logs/bot.log` | 实时查看日志 |

---

## 🎯 常见操作场景

### 场景 1: 修改配置后重启

#### Docker 部署

```bash
# 1. 停止容器
docker compose stop

# 2. 修改配置
nano config/config.json

# 3. 启动容器
docker compose start

# 4. 查看日志验证
docker compose logs -f
```

#### Systemd 部署

```bash
# 1. 停止服务
sudo systemctl stop asterdex-bot

# 2. 修改配置
nano config/config.json

# 3. 启动服务
sudo systemctl start asterdex-bot

# 4. 查看日志验证
sudo journalctl -u asterdex-bot -f
```

---

### 场景 2: 更新代码后重启

#### Docker 部署

```bash
# 1. 停止容器
docker compose stop

# 2. 拉取最新代码
git pull origin main

# 3. 重新构建镜像
docker compose build

# 4. 启动新容器
docker compose up -d

# 5. 查看日志
docker compose logs -f
```

#### Systemd 部署

```bash
# 1. 停止服务
sudo systemctl stop asterdex-bot

# 2. 备份配置
cp config/config.json config/config.backup.json

# 3. 拉取最新代码
git pull origin main

# 4. 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 5. 恢复配置
cp config/config.backup.json config/config.json

# 6. 启动服务
sudo systemctl start asterdex-bot

# 7. 查看日志
sudo journalctl -u asterdex-bot -f
```

---

### 场景 3: 紧急停止（有持仓）

**⚠️ 重要**：停止机器人**不会自动平仓**！

```bash
# 1. 立即停止机器人
docker compose stop  # 或 sudo systemctl stop asterdex-bot

# 2. 登录 AsterDEX 查看持仓
# https://www.asterdex.com/

# 3. 手动平仓（如果需要）
# 在 AsterDEX 网页端手动平仓

# 4. 确认无持仓后，可以完全删除
docker compose down
```

---

### 场景 4: 临时暂停（夜间/周末）

```bash
# 晚上睡觉前暂停
docker compose stop

# 第二天早上恢复
docker compose start

# 或使用定时任务（高级）
# 编辑 crontab
crontab -e

# 添加定时任务
# 每天 23:00 停止
0 23 * * * cd /path/to/asterdex-trading-bot && docker compose stop

# 每天 09:00 启动
0 9 * * * cd /path/to/asterdex-trading-bot && docker compose start
```

---

### 场景 5: 切换 AI 提供商

从 DeepSeek 切换到 Grok：

```bash
# 1. 停止机器人
docker compose stop

# 2. 修改配置
nano config/config.json

# 修改以下内容：
# "ai": {
#   "provider": "grok",  // 改为 "grok"
#   "grok": {
#     "api_key": "your_grok_api_key"  // 填入 Grok API Key
#   }
# }

# 3. 启动机器人
docker compose start

# 4. 查看日志确认 AI 已切换
docker compose logs -f | grep -i "grok"
```

---

### 场景 6: 完全重置

完全删除并重新开始：

```bash
# 1. 停止并删除所有容器和镜像
docker compose down --rmi all

# 2. 备份重要数据（可选）
cp config/config.json ~/backup/config.json
cp -r logs ~/backup/logs

# 3. 清理日志（可选）
rm -rf logs/*

# 4. 重新配置
cp config/config.example.json config/config.json
nano config/config.json

# 5. 重新启动
docker compose up -d
```

---

## 🔧 故障恢复

### 情况 1: 容器无法启动

```bash
# 查看详细错误
docker compose logs

# 检查配置文件
python -m json.tool config/config.json

# 检查端口占用
sudo netstat -tulpn | grep LISTEN

# 清理并重启
docker compose down
docker compose up -d
```

---

### 情况 2: 服务启动失败

```bash
# 查看详细错误
sudo journalctl -u asterdex-bot -n 100 --no-pager

# 手动测试
cd /home/user/webapp/asterdex-trading-bot
source venv/bin/activate
python src/main.py

# 检查权限
ls -la config/config.json
chmod 600 config/config.json
```

---

### 情况 3: 进程僵死

```bash
# 查找僵死进程
ps aux | grep python

# 强制杀死
kill -9 <PID>

# 或杀死所有相关进程
pkill -9 -f "python src/main.py"

# 清理并重启
docker compose down
docker compose up -d
```

---

### 情况 4: 磁盘空间不足

```bash
# 检查磁盘使用
df -h

# 清理日志
cd /home/user/webapp/asterdex-trading-bot
find logs/ -name "*.log" -mtime +7 -delete

# 清理 Docker 缓存
docker system prune -a

# 限制日志大小（修改配置）
nano config/config.json
# "logging": {
#   "max_bytes": 10485760,  # 10MB
#   "backup_count": 3       # 保留3个备份
# }
```

---

## 📊 监控运行状态

### 实时监控脚本

创建监控脚本 `monitor.sh`：

```bash
#!/bin/bash
# 实时监控机器人状态

echo "=== AsterDEX Trading Bot Status ==="
echo ""

# Docker 部署
if command -v docker &> /dev/null; then
    echo "🐳 Docker Status:"
    docker compose ps
    echo ""
    
    echo "📊 Resource Usage:"
    docker stats --no-stream asterdex-trading-bot
    echo ""
fi

# Systemd 部署
if systemctl list-unit-files | grep -q asterdex-bot; then
    echo "🖥️ Systemd Status:"
    sudo systemctl status asterdex-bot --no-pager
    echo ""
fi

# 日志摘要
echo "📝 Recent Logs (last 10 lines):"
if [ -f logs/trading_bot.log ]; then
    tail -n 10 logs/trading_bot.log
fi

echo ""
echo "✅ Monitoring complete!"
```

使用方法：

```bash
chmod +x monitor.sh
./monitor.sh
```

---

## 🔔 告警设置（可选）

### 简单邮件告警

编辑 `check_bot.sh`：

```bash
#!/bin/bash
# 检查机器人是否运行，异常时发送邮件

EMAIL="your-email@example.com"

if ! docker compose ps | grep -q "Up"; then
    echo "AsterDEX Bot is DOWN!" | mail -s "Bot Alert" $EMAIL
fi
```

添加到 crontab：

```bash
# 每5分钟检查一次
*/5 * * * * /path/to/check_bot.sh
```

---

## 📞 获取帮助

如果遇到问题：

1. 查看日志文件获取详细错误信息
2. 参考 [故障排查文档](README.md#故障排查)
3. 提交 Issue: https://github.com/MAXHONG/AsterDex-MaxTraderBot/issues

---

## ⚠️ 重要提醒

1. **停止机器人不会自动平仓**：需要手动在 AsterDEX 平仓
2. **修改配置需要重启**：配置更改后必须重启才能生效
3. **定期检查日志**：及时发现和处理异常
4. **备份配置文件**：避免误删除或损坏
5. **测试后再生产**：先用小资金测试，再正式运行

---

**最后更新**: 2025-10-22  
**文档版本**: v1.0

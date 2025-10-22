# 快速操作参考卡片

一页纸速查表 - 最常用的命令

---

## 🐳 Docker 部署（推荐）

### 基本操作

```bash
# 📂 进入目录
cd /home/user/webapp/asterdex-trading-bot

# ✅ 开启
docker compose up -d

# ⏸️ 暂停
docker compose stop

# ▶️ 恢复
docker compose start

# 🔄 重启
docker compose restart

# 📝 查看日志
docker compose logs -f

# ❌ 删除
docker compose down
```

---

## 🖥️ Systemd 服务

### 基本操作

```bash
# ✅ 开启
sudo systemctl start asterdex-bot

# ⏸️ 暂停
sudo systemctl stop asterdex-bot

# 🔄 重启
sudo systemctl restart asterdex-bot

# 📊 状态
sudo systemctl status asterdex-bot

# 📝 日志
sudo journalctl -u asterdex-bot -f
```

---

## 📋 常见场景

### 修改配置后重启

```bash
docker compose stop
nano config/config.json
docker compose start
```

### 更新代码后重启

```bash
docker compose stop
git pull
docker compose up -d --build
```

### 紧急停止

```bash
docker compose stop
# 然后登录 AsterDEX 手动平仓
```

---

## ⚠️ 重要提醒

1. **暂停不会平仓** - 需手动在 AsterDEX 平仓
2. **修改配置需重启** - 配置才会生效
3. **查看日志排错** - 第一时间查看日志

---

## 📚 详细文档

- 完整操作指南: [OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md)
- Docker 部署: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
- 主文档: [README.md](README.md)

---

**最后更新**: 2025-10-22

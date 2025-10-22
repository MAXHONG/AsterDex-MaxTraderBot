# AsterDEX Trading Bot Operations Guide

Complete guide for starting, pausing, and stopping operations

[中文文档](OPERATIONS_GUIDE.md) | [English Documentation](OPERATIONS_GUIDE_EN.md)

---

## 📋 Table of Contents

- [Docker Deployment Operations](#docker-deployment-operations)
- [Traditional Deployment Operations](#traditional-deployment-operations)
- [Quick Command Reference](#quick-command-reference)
- [Common Operation Scenarios](#common-operation-scenarios)
- [Disaster Recovery](#disaster-recovery)

---

## 🐳 Docker Deployment Operations

### 1️⃣ Start the Bot

#### First Time Start

```bash
# 1. Navigate to project directory
cd /home/user/webapp/asterdex-trading-bot

# 2. Ensure config file is ready
ls -la config/config.json

# 3. Start container (background mode)
docker compose up -d

# 4. View startup logs
docker compose logs -f
```

**Expected Output**:
```
[+] Running 1/1
 ✔ Container asterdex-trading-bot  Started
```

#### Restart Existing Container

```bash
# Method 1: Start stopped container
docker compose start

# Method 2: If container was removed, recreate and start
docker compose up -d
```

### 2️⃣ Pause the Bot

Pause means **stop trading but keep all data and configuration**.

```bash
# Stop container (keep container, can restart anytime)
docker compose stop

# Verify stopped
docker compose ps
```

**Expected Output**:
```
NAME                    STATUS
asterdex-trading-bot    Exited (0)
```

**Note**:
- ✅ Configuration preserved
- ✅ Log files preserved
- ✅ Container preserved (faster next start)
- ⚠️ Trading strategy execution stopped
- ⚠️ Won't close positions (need manual close)

### 3️⃣ Stop (Complete Removal) the Bot

Complete removal means **delete container and all runtime data**.

#### Method A: Remove Container Only (Keep Logs and Config)

```bash
# Stop and remove container
docker compose down

# Verify removed
docker compose ps -a
```

#### Method B: Complete Cleanup (Including Images)

```bash
# Stop and remove container, networks, images
docker compose down --rmi all

# Clean unused Docker resources
docker system prune -a
```

#### Method C: Total Cleanup (Including Logs and Config)

```bash
# 1. Stop and remove everything
docker compose down --rmi all

# 2. Remove logs (optional)
rm -rf logs/*

# 3. Remove config (DANGER! Backup first)
# rm config/config.json
```

**⚠️ Warning**:
- Removing container loses temporary data
- Removing images requires rebuild (time-consuming)
- Removing config requires reconfiguration

---

## 🖥️ Traditional Deployment Operations

### Using Systemd (Recommended)

#### 1️⃣ Start the Bot

```bash
# Start service
sudo systemctl start asterdex-bot

# Verify status
sudo systemctl status asterdex-bot

# View real-time logs
sudo journalctl -u asterdex-bot -f
```

**Expected Output**:
```
● asterdex-bot.service - AsterDEX Trading Bot
   Loaded: loaded (/etc/systemd/system/asterdex-bot.service; enabled)
   Active: active (running) since Wed 2025-10-22 10:30:00 UTC; 5s ago
```

#### 2️⃣ Pause the Bot

```bash
# Stop service
sudo systemctl stop asterdex-bot

# Verify stopped
sudo systemctl status asterdex-bot
```

**Expected Output**:
```
● asterdex-bot.service - AsterDEX Trading Bot
   Active: inactive (dead) since Wed 2025-10-22 10:35:00 UTC
```

#### 3️⃣ Stop the Bot

```bash
# Stop service
sudo systemctl stop asterdex-bot

# Disable auto-start
sudo systemctl disable asterdex-bot

# Remove service file (optional)
sudo rm /etc/systemd/system/asterdex-bot.service
sudo systemctl daemon-reload
```

---

### Using nohup (Simple Method)

#### 1️⃣ Start the Bot

```bash
# Navigate to project directory
cd /home/user/webapp/asterdex-trading-bot

# Activate virtual environment
source venv/bin/activate

# Run in background
nohup python src/main.py > logs/bot.log 2>&1 &

# Save process ID
echo $! > bot.pid

# View logs
tail -f logs/bot.log
```

#### 2️⃣ Pause the Bot

```bash
# Find process ID
ps aux | grep "python src/main.py"

# Method 1: Use saved PID
kill $(cat bot.pid)

# Method 2: Manual kill
kill <PID>

# Verify stopped
ps aux | grep "python src/main.py"
```

#### 3️⃣ Stop the Bot

```bash
# Force kill
kill -9 $(cat bot.pid)

# Or find and kill manually
pkill -f "python src/main.py"

# Clean up PID file
rm bot.pid
```

---

### Direct Run (Development Mode)

#### 1️⃣ Start the Bot

```bash
# Navigate to project directory
cd /home/user/webapp/asterdex-trading-bot

# Activate virtual environment
source venv/bin/activate

# Run in foreground (see real-time output)
python src/main.py
```

#### 2️⃣ Pause/Stop the Bot

```bash
# Press Ctrl + C to stop
# Bot will shutdown gracefully
```

---

## ⚡ Quick Command Reference

### Docker Deployment

| Operation | Command | Description |
|-----------|---------|-------------|
| **Start** | `docker compose up -d` | Start in background |
| **Start (with logs)** | `docker compose up` | Start in foreground, show logs |
| **Pause** | `docker compose stop` | Stop container, keep data |
| **Resume** | `docker compose start` | Restart stopped container |
| **Restart** | `docker compose restart` | Restart container |
| **Remove** | `docker compose down` | Remove container, keep image |
| **Complete Remove** | `docker compose down --rmi all` | Remove container and images |
| **Status** | `docker compose ps` | View container status |
| **Logs** | `docker compose logs -f` | Real-time logs |
| **Enter Container** | `docker compose exec asterdex-bot bash` | Enter for debugging |

### Systemd Service

| Operation | Command | Description |
|-----------|---------|-------------|
| **Start** | `sudo systemctl start asterdex-bot` | Start service |
| **Pause** | `sudo systemctl stop asterdex-bot` | Stop service |
| **Restart** | `sudo systemctl restart asterdex-bot` | Restart service |
| **Status** | `sudo systemctl status asterdex-bot` | Check status |
| **Enable Auto-start** | `sudo systemctl enable asterdex-bot` | Enable auto-start |
| **Disable Auto-start** | `sudo systemctl disable asterdex-bot` | Disable auto-start |
| **Logs** | `sudo journalctl -u asterdex-bot -f` | Real-time logs |
| **Recent Logs** | `sudo journalctl -u asterdex-bot -n 100` | Last 100 lines |

### Process Management (nohup)

| Operation | Command | Description |
|-----------|---------|-------------|
| **Start** | `nohup python src/main.py > logs/bot.log 2>&1 &` | Start in background |
| **Find Process** | `ps aux \| grep "python src/main.py"` | Find process ID |
| **Stop** | `kill $(cat bot.pid)` | Graceful stop |
| **Force Stop** | `kill -9 $(cat bot.pid)` | Force stop |
| **View Logs** | `tail -f logs/bot.log` | Real-time logs |

---

## 🎯 Common Operation Scenarios

### Scenario 1: Restart After Config Change

#### Docker Deployment

```bash
# 1. Stop container
docker compose stop

# 2. Edit config
nano config/config.json

# 3. Start container
docker compose start

# 4. Verify in logs
docker compose logs -f
```

#### Systemd Deployment

```bash
# 1. Stop service
sudo systemctl stop asterdex-bot

# 2. Edit config
nano config/config.json

# 3. Start service
sudo systemctl start asterdex-bot

# 4. Verify in logs
sudo journalctl -u asterdex-bot -f
```

---

### Scenario 2: Restart After Code Update

#### Docker Deployment

```bash
# 1. Stop container
docker compose stop

# 2. Pull latest code
git pull origin main

# 3. Rebuild image
docker compose build

# 4. Start new container
docker compose up -d

# 5. View logs
docker compose logs -f
```

#### Systemd Deployment

```bash
# 1. Stop service
sudo systemctl stop asterdex-bot

# 2. Backup config
cp config/config.json config/config.backup.json

# 3. Pull latest code
git pull origin main

# 4. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 5. Restore config
cp config/config.backup.json config/config.json

# 6. Start service
sudo systemctl start asterdex-bot

# 7. View logs
sudo journalctl -u asterdex-bot -f
```

---

### Scenario 3: Emergency Stop (With Open Positions)

**⚠️ Important**: Stopping bot **won't auto-close positions**!

```bash
# 1. Stop bot immediately
docker compose stop  # or sudo systemctl stop asterdex-bot

# 2. Login to AsterDEX to check positions
# https://www.asterdex.com/

# 3. Manually close positions (if needed)
# Close positions in AsterDEX web interface

# 4. After confirming no positions, complete removal
docker compose down
```

---

### Scenario 4: Temporary Pause (Night/Weekend)

```bash
# Pause before sleep
docker compose stop

# Resume next morning
docker compose start

# Or use scheduled tasks (advanced)
# Edit crontab
crontab -e

# Add scheduled tasks
# Stop at 23:00 daily
0 23 * * * cd /path/to/asterdex-trading-bot && docker compose stop

# Start at 09:00 daily
0 9 * * * cd /path/to/asterdex-trading-bot && docker compose start
```

---

### Scenario 5: Switch AI Provider

Switch from DeepSeek to Grok:

```bash
# 1. Stop bot
docker compose stop

# 2. Edit config
nano config/config.json

# Modify:
# "ai": {
#   "provider": "grok",  // Change to "grok"
#   "grok": {
#     "api_key": "your_grok_api_key"  // Fill in Grok API Key
#   }
# }

# 3. Start bot
docker compose start

# 4. Verify AI switch in logs
docker compose logs -f | grep -i "grok"
```

---

### Scenario 6: Complete Reset

Complete removal and fresh start:

```bash
# 1. Stop and remove everything
docker compose down --rmi all

# 2. Backup important data (optional)
cp config/config.json ~/backup/config.json
cp -r logs ~/backup/logs

# 3. Clean logs (optional)
rm -rf logs/*

# 4. Reconfigure
cp config/config.example.json config/config.json
nano config/config.json

# 5. Restart
docker compose up -d
```

---

## 🔧 Disaster Recovery

### Case 1: Container Won't Start

```bash
# View detailed errors
docker compose logs

# Check config file
python -m json.tool config/config.json

# Check port usage
sudo netstat -tulpn | grep LISTEN

# Clean and restart
docker compose down
docker compose up -d
```

---

### Case 2: Service Start Failed

```bash
# View detailed errors
sudo journalctl -u asterdex-bot -n 100 --no-pager

# Manual test
cd /home/user/webapp/asterdex-trading-bot
source venv/bin/activate
python src/main.py

# Check permissions
ls -la config/config.json
chmod 600 config/config.json
```

---

### Case 3: Zombie Process

```bash
# Find zombie process
ps aux | grep python

# Force kill
kill -9 <PID>

# Or kill all related processes
pkill -9 -f "python src/main.py"

# Clean and restart
docker compose down
docker compose up -d
```

---

### Case 4: Disk Space Full

```bash
# Check disk usage
df -h

# Clean logs
cd /home/user/webapp/asterdex-trading-bot
find logs/ -name "*.log" -mtime +7 -delete

# Clean Docker cache
docker system prune -a

# Limit log size (edit config)
nano config/config.json
# "logging": {
#   "max_bytes": 10485760,  # 10MB
#   "backup_count": 3       # Keep 3 backups
# }
```

---

## 📊 Monitor Running Status

### Real-time Monitoring Script

Create `monitor.sh`:

```bash
#!/bin/bash
# Real-time bot status monitoring

echo "=== AsterDEX Trading Bot Status ==="
echo ""

# Docker deployment
if command -v docker &> /dev/null; then
    echo "🐳 Docker Status:"
    docker compose ps
    echo ""
    
    echo "📊 Resource Usage:"
    docker stats --no-stream asterdex-trading-bot
    echo ""
fi

# Systemd deployment
if systemctl list-unit-files | grep -q asterdex-bot; then
    echo "🖥️ Systemd Status:"
    sudo systemctl status asterdex-bot --no-pager
    echo ""
fi

# Log summary
echo "📝 Recent Logs (last 10 lines):"
if [ -f logs/trading_bot.log ]; then
    tail -n 10 logs/trading_bot.log
fi

echo ""
echo "✅ Monitoring complete!"
```

Usage:

```bash
chmod +x monitor.sh
./monitor.sh
```

---

## 🔔 Alert Setup (Optional)

### Simple Email Alert

Edit `check_bot.sh`:

```bash
#!/bin/bash
# Check if bot is running, send email on failure

EMAIL="your-email@example.com"

if ! docker compose ps | grep -q "Up"; then
    echo "AsterDEX Bot is DOWN!" | mail -s "Bot Alert" $EMAIL
fi
```

Add to crontab:

```bash
# Check every 5 minutes
*/5 * * * * /path/to/check_bot.sh
```

---

## 📞 Getting Help

If you encounter issues:

1. Check log files for detailed error messages
2. Refer to [Troubleshooting Guide](README_EN.md#troubleshooting)
3. Submit Issue: https://github.com/MAXHONG/AsterDex-MaxTraderBot/issues

---

## ⚠️ Important Reminders

1. **Stopping bot won't auto-close positions**: Manual close required in AsterDEX
2. **Config changes need restart**: Must restart for changes to take effect
3. **Check logs regularly**: Detect and handle issues promptly
4. **Backup config files**: Avoid accidental deletion or corruption
5. **Test before production**: Test with small amounts first

---

**Last Updated**: 2025-10-22  
**Document Version**: v1.0

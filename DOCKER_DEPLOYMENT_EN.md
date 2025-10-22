# Docker Deployment Guide

[中文文档](DOCKER_DEPLOYMENT.md)

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Deployment Methods](#deployment-methods)
- [Operations Management](#operations-management)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)

## Prerequisites

### System Requirements

- Docker 20.10+
- Docker Compose 2.0+ (optional, for docker-compose deployment)
- At least 512MB available memory
- Stable network connection

### Installing Docker

**Ubuntu/Debian:**
```bash
# Update package index
sudo apt-get update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

**CentOS/RHEL:**
```bash
# Install Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
docker --version
docker compose version
```

**macOS:**
```bash
# Using Homebrew
brew install --cask docker

# Or download Docker Desktop
# https://www.docker.com/products/docker-desktop
```

**Windows:**
- Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
- Enable WSL2 backend (recommended)

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/MAXHONG/AsterDex-MaxTraderBot.git
cd AsterDex-MaxTraderBot/asterdex-trading-bot
```

### 2. Configuration

Copy configuration template and edit:

```bash
# Method 1: Using JSON config file (recommended)
cp config/config.example.json config/config.json
nano config/config.json
```

Or

```bash
# Method 2: Using environment variables
cp .env.example .env
nano .env
```

**Required Configuration:**

```json
{
  "asterdex": {
    "user": "your_main_wallet_address",
    "signer": "your_api_wallet_address",
    "private_key": "your_api_wallet_private_key",
    "api_base_url": "https://fapi.asterdex.com"
  },
  "ai": {
    "provider": "deepseek",
    "deepseek": {
      "api_key": "your_deepseek_api_key",
      "api_base_url": "https://api.deepseek.com",
      "model": "deepseek-chat"
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

### 3. Build and Run

**Using Docker Compose (Recommended):**

```bash
# Build image
docker compose build

# Start container (detached mode)
docker compose up -d

# View logs
docker compose logs -f

# Stop container
docker compose down
```

**Using Docker Commands:**

```bash
# Build image
docker build -t asterdex-bot:latest .

# Run container
docker run -d \
  --name asterdex-trading-bot \
  --restart unless-stopped \
  -v $(pwd)/config/config.json:/app/config/config.json:ro \
  -v $(pwd)/logs:/app/logs \
  asterdex-bot:latest

# View logs
docker logs -f asterdex-trading-bot

# Stop container
docker stop asterdex-trading-bot
docker rm asterdex-trading-bot
```

## Configuration

### Configuration Methods Comparison

| Method | Pros | Cons | Use Case |
|--------|------|------|----------|
| JSON Config File | Clear structure, easy to manage complex configs | Requires file mounting | Production, multi-environment |
| Environment Variables | CI/CD friendly, cloud-native | Hard to manage with many variables | Containerized, automated deployment |

### AI Provider Configuration

**Option 1: DeepSeek (Recommended)**

```json
{
  "ai": {
    "provider": "deepseek",
    "deepseek": {
      "api_key": "sk-xxx",
      "api_base_url": "https://api.deepseek.com",
      "model": "deepseek-chat",
      "timeout": 30
    }
  }
}
```

**Option 2: Grok**

```json
{
  "ai": {
    "provider": "grok",
    "grok": {
      "api_key": "xai-xxx",
      "api_base_url": "https://api.x.ai/v1",
      "model": "grok-beta",
      "timeout": 30
    }
  }
}
```

### Volume Mounts

| Mount Point | Type | Description | Required |
|-------------|------|-------------|----------|
| `/app/config/config.json` | File | Configuration file (read-only) | ✅ |
| `/app/logs` | Directory | Persistent logs | Recommended |
| `/app/src/strategies/custom` | Directory | Custom strategies (read-only) | Optional |

## Deployment Methods

### Method 1: Docker Compose (Recommended)

**Advantages:**
- Configuration as code, easy version control
- One-command start/stop
- Built-in health checks and resource limits
- Suitable for multi-container orchestration

**Steps:**

```bash
# 1. Edit configuration
nano config/config.json

# 2. Start services
docker compose up -d

# 3. Verify running
docker compose ps
docker compose logs -f asterdex-bot

# 4. Restart after config changes
docker compose restart asterdex-bot

# 5. Stop and cleanup
docker compose down
```

### Method 2: Docker Commands

**Advantages:**
- More flexible runtime control
- Suitable for single container deployment
- Scriptable deployment

**Start Script Example (`start.sh`):**

```bash
#!/bin/bash

# Configuration variables
IMAGE_NAME="asterdex-bot"
CONTAINER_NAME="asterdex-trading-bot"
CONFIG_PATH="$(pwd)/config/config.json"
LOG_PATH="$(pwd)/logs"

# Stop old container
docker stop $CONTAINER_NAME 2>/dev/null
docker rm $CONTAINER_NAME 2>/dev/null

# Build image
docker build -t $IMAGE_NAME:latest .

# Start container
docker run -d \
  --name $CONTAINER_NAME \
  --restart unless-stopped \
  -v $CONFIG_PATH:/app/config/config.json:ro \
  -v $LOG_PATH:/app/logs \
  -e TZ=Asia/Shanghai \
  --memory=512m \
  --cpus=1.0 \
  $IMAGE_NAME:latest

echo "✅ Container started: $CONTAINER_NAME"
docker logs -f $CONTAINER_NAME
```

### Method 3: Docker Swarm / Kubernetes

**Docker Swarm Example:**

```yaml
# stack.yml
version: '3.8'

services:
  asterdex-bot:
    image: asterdex-bot:latest
    deploy:
      replicas: 1
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
    configs:
      - source: bot-config
        target: /app/config/config.json
    volumes:
      - bot-logs:/app/logs

configs:
  bot-config:
    file: ./config/config.json

volumes:
  bot-logs:
```

Deploy command:
```bash
docker stack deploy -c stack.yml asterdex-bot-stack
```

## Operations Management

### Daily Operations

**Check Status:**
```bash
# Docker Compose
docker compose ps

# Docker command
docker ps -f name=asterdex-trading-bot
```

**View Logs:**
```bash
# Real-time logs
docker compose logs -f asterdex-bot

# Last 100 lines
docker compose logs --tail=100 asterdex-bot

# View log file inside container
docker exec asterdex-trading-bot tail -f /app/logs/trading_bot.log
```

**Restart Service:**
```bash
# Soft restart (no container recreation)
docker compose restart asterdex-bot

# Hard restart (recreate container)
docker compose up -d --force-recreate asterdex-bot
```

**Update Configuration:**
```bash
# 1. Edit config file
nano config/config.json

# 2. Restart container to apply changes
docker compose restart asterdex-bot
```

**Update Code:**
```bash
# 1. Pull latest code
git pull

# 2. Rebuild image
docker compose build

# 3. Restart service
docker compose up -d
```

### Backup and Restore

**Backup Config and Logs:**
```bash
# Create backup directory
mkdir -p backups/$(date +%Y%m%d)

# Backup config
cp config/config.json backups/$(date +%Y%m%d)/

# Backup logs
tar -czf backups/$(date +%Y%m%d)/logs.tar.gz logs/
```

**Restore:**
```bash
# Restore config
cp backups/20241022/config.json config/

# Restore logs
tar -xzf backups/20241022/logs.tar.gz
```

### Monitoring and Alerting

**Health Check:**
```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' asterdex-trading-bot

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' asterdex-trading-bot
```

**Resource Usage Monitoring:**
```bash
# Real-time monitoring
docker stats asterdex-trading-bot

# One-time check
docker stats --no-stream asterdex-trading-bot
```

**Integrate Monitoring System (Optional):**

Using Prometheus + Grafana to monitor Docker containers:

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  asterdex-bot:
    # ... existing config ...
    labels:
      - "prometheus.scrape=true"
      - "prometheus.port=8080"

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  prometheus-data:
  grafana-data:
```

## Troubleshooting

### Common Issues

**1. Container Won't Start**

```bash
# View container logs
docker compose logs asterdex-bot

# View detailed error
docker logs asterdex-trading-bot

# Check config
docker compose config
```

Possible causes:
- Config file format error (JSON syntax)
- Incorrect config file path
- Missing required config fields
- Port conflicts

**2. Permission Errors**

```bash
# Check file permissions
ls -la config/config.json
ls -la logs/

# Fix permissions
chmod 600 config/config.json  # Config file
chmod 755 logs/               # Log directory
```

**3. Network Issues**

```bash
# Test API connectivity
docker exec asterdex-trading-bot ping -c 3 fapi.asterdex.com
docker exec asterdex-trading-bot ping -c 3 api.deepseek.com

# Check DNS resolution
docker exec asterdex-trading-bot nslookup fapi.asterdex.com
```

**4. Out of Memory**

```bash
# Check resource usage
docker stats asterdex-trading-bot

# Increase memory limit (docker-compose.yml)
deploy:
  resources:
    limits:
      memory: 1G  # Increase from 512M to 1G
```

**5. Time Sync Issues**

```bash
# Check container time
docker exec asterdex-trading-bot date

# Ensure host time is correct
sudo ntpdate -u pool.ntp.org

# Set timezone in docker-compose.yml
environment:
  - TZ=Asia/Shanghai
```

### Debug Mode

**Start Debug Mode:**

```bash
# Method 1: Interactive run
docker run -it --rm \
  -v $(pwd)/config/config.json:/app/config/config.json:ro \
  -v $(pwd)/logs:/app/logs \
  asterdex-bot:latest \
  /bin/bash

# Method 2: Override entrypoint
docker compose run --rm asterdex-bot /bin/bash

# Method 3: Enter running container
docker exec -it asterdex-trading-bot /bin/bash
```

**Debug Inside Container:**

```bash
# Check Python environment
python --version
pip list

# Test imports
python -c "from src.api.asterdex_client import AsterDexClient; print('OK')"

# Run manually
python src/main.py

# Check processes
ps aux | grep python
```

### Log Analysis

**Log Levels:**
```json
{
  "logging": {
    "level": "DEBUG",  // DEBUG, INFO, WARNING, ERROR, CRITICAL
    "file": "/app/logs/trading_bot.log"
  }
}
```

**Search Specific Errors:**
```bash
# Search error logs
docker exec asterdex-trading-bot grep "ERROR" /app/logs/trading_bot.log

# Search signature errors
docker exec asterdex-trading-bot grep "signature" /app/logs/trading_bot.log -i

# Recent warnings
docker exec asterdex-trading-bot grep "WARNING" /app/logs/trading_bot.log | tail -20
```

## Security Best Practices

### Configuration File Security

```bash
# 1. Set strict file permissions
chmod 600 config/config.json
chmod 700 config/

# 2. Don't commit config to version control
echo "config/config.json" >> .gitignore

# 3. Use secrets for sensitive data (Docker Swarm)
docker secret create asterdex_private_key ./private_key.txt
```

### Container Security

```yaml
# docker-compose.yml security config
services:
  asterdex-bot:
    # 1. Read-only root filesystem
    read_only: true
    tmpfs:
      - /tmp
      - /app/logs
    
    # 2. Drop unnecessary capabilities
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    
    # 3. Use non-root user (configured in Dockerfile)
    user: "1000:1000"
    
    # 4. Limit resources
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
    
    # 5. Disable privileged mode
    privileged: false
    
    # 6. Security options
    security_opt:
      - no-new-privileges:true
```

### Network Security

```yaml
# Use custom network isolation
networks:
  bot-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16

services:
  asterdex-bot:
    networks:
      - bot-network
    # Don't expose ports (unless API needed)
    # ports: []
```

### Secret Management Best Practices

1. **Use Environment Variables + Secrets:**
```bash
# Load environment variables from file
docker compose --env-file .env.production up -d
```

2. **Use Docker Secrets (Swarm):**
```yaml
secrets:
  asterdex_private_key:
    external: true
  deepseek_api_key:
    external: true

services:
  asterdex-bot:
    secrets:
      - asterdex_private_key
      - deepseek_api_key
```

3. **Use External Secret Management:**
- HashiCorp Vault
- AWS Secrets Manager
- Azure Key Vault
- Google Secret Manager

### Regular Security Updates

```bash
# 1. Update base image
docker pull python:3.11-slim

# 2. Rebuild
docker compose build --no-cache

# 3. Scan image vulnerabilities
docker scan asterdex-bot:latest

# Or use Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image asterdex-bot:latest
```

## Production Deployment Checklist

- [ ] Configuration file properly filled and verified
- [ ] Private key file permissions set to 600
- [ ] Log persistence enabled
- [ ] Resource limits configured (CPU/memory)
- [ ] Health checks enabled
- [ ] Auto-restart policy configured
- [ ] Appropriate timezone set
- [ ] Log rotation configured
- [ ] Monitoring and alerting set up
- [ ] Tested with small funds
- [ ] Backup and restore plan prepared
- [ ] Troubleshooting process understood

## Related Documentation

- [Main Documentation (README_EN.md)](README_EN.md)
- [Deployment Guide (DEPLOYMENT_GUIDE_EN.md)](DEPLOYMENT_GUIDE_EN.md)
- [Quick Start (QUICKSTART_EN.md)](QUICKSTART_EN.md)
- [AI Enhancement System (AI_ENHANCEMENT_IMPLEMENTATION_COMPLETE.md)](AI_ENHANCEMENT_IMPLEMENTATION_COMPLETE.md)

## Technical Support

If you encounter issues:

1. Check [Troubleshooting](#troubleshooting) section
2. Review GitHub Issues: https://github.com/MAXHONG/AsterDex-MaxTraderBot/issues
3. Check container logs for detailed error messages

## License

MIT License

## Disclaimer

This software is for educational and research purposes only. All risks of using this software for actual trading are borne by the user. Developers are not responsible for any trading losses.

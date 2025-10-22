# Docker 部署指南

[English Documentation](DOCKER_DEPLOYMENT_EN.md)

## 目录

- [前提条件](#前提条件)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [部署方式](#部署方式)
- [运维管理](#运维管理)
- [故障排查](#故障排查)
- [安全建议](#安全建议)

## 前提条件

### 系统要求

- Docker 20.10+ 
- Docker Compose 2.0+ (可选，用于 docker-compose 部署)
- 至少 512MB 可用内存
- 稳定的网络连接

### 安装 Docker

**Ubuntu/Debian:**
```bash
# 更新包索引
sudo apt-get update

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo apt-get install docker-compose-plugin

# 验证安装
docker --version
docker compose version
```

**CentOS/RHEL:**
```bash
# 安装 Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
docker compose version
```

**macOS:**
```bash
# 使用 Homebrew
brew install --cask docker

# 或下载 Docker Desktop
# https://www.docker.com/products/docker-desktop
```

**Windows:**
- 下载并安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
- 启用 WSL2 后端 (推荐)

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/MAXHONG/AsterDex-MaxTraderBot.git
cd AsterDex-MaxTraderBot/asterdex-trading-bot
```

### 2. 配置文件

复制配置模板并编辑：

```bash
# 方式 1: 使用 JSON 配置文件 (推荐)
cp config/config.example.json config/config.json
nano config/config.json
```

或

```bash
# 方式 2: 使用环境变量
cp .env.example .env
nano .env
```

**必填配置项:**

```json
{
  "asterdex": {
    "user": "你的主钱包地址",
    "signer": "API钱包地址",
    "private_key": "API钱包私钥",
    "api_base_url": "https://fapi.asterdex.com"
  },
  "ai": {
    "provider": "deepseek",
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
  }
}
```

### 3. 构建并启动

**使用 Docker Compose (推荐):**

```bash
# 构建镜像
docker compose build

# 启动容器 (后台运行)
docker compose up -d

# 查看日志
docker compose logs -f

# 停止容器
docker compose down
```

**使用 Docker 命令:**

```bash
# 构建镜像
docker build -t asterdex-bot:latest .

# 运行容器
docker run -d \
  --name asterdex-trading-bot \
  --restart unless-stopped \
  -v $(pwd)/config/config.json:/app/config/config.json:ro \
  -v $(pwd)/logs:/app/logs \
  asterdex-bot:latest

# 查看日志
docker logs -f asterdex-trading-bot

# 停止容器
docker stop asterdex-trading-bot
docker rm asterdex-trading-bot
```

## 配置说明

### 配置方式对比

| 方式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| JSON 配置文件 | 结构清晰，易于管理复杂配置 | 需要挂载文件 | 生产环境，多环境部署 |
| 环境变量 | 适合 CI/CD，云原生 | 配置项多时不易管理 | 容器化部署，自动化部署 |

### AI 提供商配置

**选项 1: DeepSeek (推荐)**

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

**选项 2: Grok**

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

### 卷挂载说明

| 挂载点 | 类型 | 说明 | 必需 |
|--------|------|------|------|
| `/app/config/config.json` | 文件 | 配置文件 (只读) | ✅ |
| `/app/logs` | 目录 | 日志持久化 | 推荐 |
| `/app/src/strategies/custom` | 目录 | 自定义策略 (只读) | 可选 |

## 部署方式

### 方式 1: Docker Compose (推荐)

**优点:**
- 配置文件化，易于版本管理
- 一键启动/停止
- 内置健康检查和资源限制
- 适合多容器编排

**步骤:**

```bash
# 1. 编辑配置
nano config/config.json

# 2. 启动服务
docker compose up -d

# 3. 验证运行
docker compose ps
docker compose logs -f asterdex-bot

# 4. 更新配置后重启
docker compose restart asterdex-bot

# 5. 完全停止并清理
docker compose down
```

### 方式 2: Docker 命令

**优点:**
- 更灵活的运行时控制
- 适合单容器部署
- 脚本化部署

**启动脚本示例 (`start.sh`):**

```bash
#!/bin/bash

# 配置变量
IMAGE_NAME="asterdex-bot"
CONTAINER_NAME="asterdex-trading-bot"
CONFIG_PATH="$(pwd)/config/config.json"
LOG_PATH="$(pwd)/logs"

# 停止旧容器
docker stop $CONTAINER_NAME 2>/dev/null
docker rm $CONTAINER_NAME 2>/dev/null

# 构建镜像
docker build -t $IMAGE_NAME:latest .

# 启动容器
docker run -d \
  --name $CONTAINER_NAME \
  --restart unless-stopped \
  -v $CONFIG_PATH:/app/config/config.json:ro \
  -v $LOG_PATH:/app/logs \
  -e TZ=Asia/Shanghai \
  --memory=512m \
  --cpus=1.0 \
  $IMAGE_NAME:latest

echo "✅ 容器已启动: $CONTAINER_NAME"
docker logs -f $CONTAINER_NAME
```

### 方式 3: Docker Swarm / Kubernetes

**Docker Swarm 示例:**

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

部署命令:
```bash
docker stack deploy -c stack.yml asterdex-bot-stack
```

## 运维管理

### 日常操作

**查看运行状态:**
```bash
# Docker Compose
docker compose ps

# Docker 命令
docker ps -f name=asterdex-trading-bot
```

**查看日志:**
```bash
# 实时日志
docker compose logs -f asterdex-bot

# 最近100行
docker compose logs --tail=100 asterdex-bot

# 查看容器内日志文件
docker exec asterdex-trading-bot tail -f /app/logs/trading_bot.log
```

**重启服务:**
```bash
# 软重启 (不重新创建容器)
docker compose restart asterdex-bot

# 硬重启 (重新创建容器)
docker compose up -d --force-recreate asterdex-bot
```

**更新配置:**
```bash
# 1. 编辑配置文件
nano config/config.json

# 2. 重启容器以应用新配置
docker compose restart asterdex-bot
```

**更新代码:**
```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建镜像
docker compose build

# 3. 重启服务
docker compose up -d
```

### 备份与恢复

**备份配置和日志:**
```bash
# 创建备份目录
mkdir -p backups/$(date +%Y%m%d)

# 备份配置
cp config/config.json backups/$(date +%Y%m%d)/

# 备份日志
tar -czf backups/$(date +%Y%m%d)/logs.tar.gz logs/
```

**恢复:**
```bash
# 恢复配置
cp backups/20241022/config.json config/

# 恢复日志
tar -xzf backups/20241022/logs.tar.gz
```

### 监控和告警

**健康检查:**
```bash
# 查看健康状态
docker inspect --format='{{.State.Health.Status}}' asterdex-trading-bot

# 查看健康检查日志
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' asterdex-trading-bot
```

**资源使用监控:**
```bash
# 实时监控
docker stats asterdex-trading-bot

# 一次性查看
docker stats --no-stream asterdex-trading-bot
```

**集成监控系统 (可选):**

使用 Prometheus + Grafana 监控 Docker 容器:

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  asterdex-bot:
    # ... 原有配置 ...
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

## 故障排查

### 常见问题

**1. 容器无法启动**

```bash
# 查看容器日志
docker compose logs asterdex-bot

# 查看详细错误信息
docker logs asterdex-trading-bot

# 检查配置文件
docker compose config
```

可能原因:
- 配置文件格式错误 (JSON 语法)
- 配置文件路径不正确
- 必填配置项缺失
- 端口冲突

**2. 权限错误**

```bash
# 检查文件权限
ls -la config/config.json
ls -la logs/

# 修复权限
chmod 600 config/config.json  # 配置文件
chmod 755 logs/               # 日志目录
```

**3. 网络问题**

```bash
# 测试 API 连接
docker exec asterdex-trading-bot ping -c 3 fapi.asterdex.com
docker exec asterdex-trading-bot ping -c 3 api.deepseek.com

# 检查 DNS 解析
docker exec asterdex-trading-bot nslookup fapi.asterdex.com
```

**4. 内存不足**

```bash
# 检查资源使用
docker stats asterdex-trading-bot

# 增加内存限制 (docker-compose.yml)
deploy:
  resources:
    limits:
      memory: 1G  # 从 512M 增加到 1G
```

**5. 时间同步问题**

```bash
# 检查容器时间
docker exec asterdex-trading-bot date

# 确保宿主机时间正确
sudo ntpdate -u pool.ntp.org

# 在 docker-compose.yml 中设置时区
environment:
  - TZ=Asia/Shanghai
```

### 调试模式

**启动调试模式:**

```bash
# 方式 1: 交互式运行
docker run -it --rm \
  -v $(pwd)/config/config.json:/app/config/config.json:ro \
  -v $(pwd)/logs:/app/logs \
  asterdex-bot:latest \
  /bin/bash

# 方式 2: 覆盖入口点
docker compose run --rm asterdex-bot /bin/bash

# 方式 3: 进入运行中的容器
docker exec -it asterdex-trading-bot /bin/bash
```

**在容器内调试:**

```bash
# 检查 Python 环境
python --version
pip list

# 测试导入
python -c "from src.api.asterdex_client import AsterDexClient; print('OK')"

# 手动运行程序
python src/main.py

# 查看进程
ps aux | grep python
```

### 日志分析

**日志级别:**
```json
{
  "logging": {
    "level": "DEBUG",  // DEBUG, INFO, WARNING, ERROR, CRITICAL
    "file": "/app/logs/trading_bot.log"
  }
}
```

**搜索特定错误:**
```bash
# 搜索错误日志
docker exec asterdex-trading-bot grep "ERROR" /app/logs/trading_bot.log

# 搜索签名错误
docker exec asterdex-trading-bot grep "signature" /app/logs/trading_bot.log -i

# 最近的警告
docker exec asterdex-trading-bot grep "WARNING" /app/logs/trading_bot.log | tail -20
```

## 安全建议

### 配置文件安全

```bash
# 1. 设置严格的文件权限
chmod 600 config/config.json
chmod 700 config/

# 2. 不要提交配置文件到版本控制
echo "config/config.json" >> .gitignore

# 3. 使用 secrets 管理敏感信息 (Docker Swarm)
docker secret create asterdex_private_key ./private_key.txt
```

### 容器安全

```yaml
# docker-compose.yml 安全配置
services:
  asterdex-bot:
    # 1. 只读根文件系统
    read_only: true
    tmpfs:
      - /tmp
      - /app/logs
    
    # 2. 删除不必要的能力
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    
    # 3. 使用非 root 用户 (已在 Dockerfile 中配置)
    user: "1000:1000"
    
    # 4. 限制资源
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
    
    # 5. 禁用特权模式
    privileged: false
    
    # 6. 安全选项
    security_opt:
      - no-new-privileges:true
```

### 网络安全

```yaml
# 使用自定义网络隔离
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
    # 不暴露端口 (除非需要 API)
    # ports: []
```

### 密钥管理最佳实践

1. **使用环境变量 + Secrets:**
```bash
# 从文件加载环境变量
docker compose --env-file .env.production up -d
```

2. **使用 Docker Secrets (Swarm):**
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

3. **使用外部密钥管理系统:**
- HashiCorp Vault
- AWS Secrets Manager
- Azure Key Vault
- Google Secret Manager

### 定期安全更新

```bash
# 1. 更新基础镜像
docker pull python:3.11-slim

# 2. 重新构建
docker compose build --no-cache

# 3. 扫描镜像漏洞
docker scan asterdex-bot:latest

# 或使用 Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image asterdex-bot:latest
```

## 生产环境部署清单

- [ ] 配置文件已正确填写并验证
- [ ] 私钥文件权限设置为 600
- [ ] 启用了日志持久化
- [ ] 配置了资源限制 (CPU/内存)
- [ ] 启用了健康检查
- [ ] 配置了自动重启策略
- [ ] 设置了合理的时区
- [ ] 启用了日志轮转
- [ ] 配置了监控和告警
- [ ] 进行了小额资金测试
- [ ] 准备了备份和恢复方案
- [ ] 了解故障排查流程

## 相关文档

- [主文档 (README.md)](README.md)
- [部署指南 (DEPLOYMENT_GUIDE.md)](DEPLOYMENT_GUIDE.md)
- [快速开始 (QUICKSTART.md)](QUICKSTART.md)
- [AI 增强系统 (AI_ENHANCEMENT_IMPLEMENTATION_COMPLETE.md)](AI_ENHANCEMENT_IMPLEMENTATION_COMPLETE.md)

## 技术支持

如遇到问题，请:

1. 查看 [故障排查](#故障排查) 章节
2. 检查 GitHub Issues: https://github.com/MAXHONG/AsterDex-MaxTraderBot/issues
3. 查看容器日志获取详细错误信息

## 许可证

MIT License

## 免责声明

本软件仅供学习和研究使用。使用本软件进行实际交易的所有风险由用户自行承担。开发者不对任何交易损失负责。

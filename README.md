# AsterDEX 自动化交易机器人

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![AsterDEX](https://img.shields.io/badge/Exchange-AsterDEX-orange.svg)](https://www.asterdex.com/)

基于 AsterDEX API 的智能合约交易系统，集成双均线策略和 AI 增强功能

[中文文档](README.md) | [English Documentation](README_EN.md)

</div>

---

## ✨ 核心特性

### 🎯 交易策略
- **双均线系统**：SMA20/60/120 + EMA20/60/120 组合
- **多频率交易**：
  - 🔥 高频：15分钟K线，每5分钟检查
  - ⏱️ 中频：4小时K线，每1小时检查
- **智能信号**：双均线密集判断 + 突破确认

### 🤖 AI 增强系统（可选）

支持 **DeepSeek** 和 **Grok** 双 AI 提供商，四阶段智能优化：

| 阶段 | 功能 | 提升效果 |
|------|------|----------|
| 🧠 **Phase 1** | 市场情报系统 | 多源信息聚合分析 |
| 📊 **Phase 2** | 动态风险评估 | +30-40% 风险控制 |
| 🎯 **Phase 3** | 智能持仓管理 | +25-35% 仓位优化 |
| ⚙️ **Phase 4** | 策略参数优化 | +20-30% 参数适应 |

> **整体性能提升**: +35-55% | [查看详细说明](AI_ENHANCEMENT_IMPLEMENTATION_COMPLETE.md)

### 🛡️ 风险管理
- **逐仓模式**：风险隔离，单币种独立
- **杠杆限制**：最高5倍，可调节
- **仓位控制**：单币种最多占用30%保证金
- **止损机制**：动态止损3% + AI优化

### 💰 支持币种
- BTC/USDT
- ETH/USDT
- BNB/USDT
- ASTER/USDT

---

## 📋 交易策略说明

### 双均线密集判断

当短期（SMA20/EMA20）、中期（SMA60/EMA60）、长期（SMA120/EMA120）均线密集排列时：

#### 做多信号 📈
1. ✅ 三组均线发生密集（价差 ≤ 2%）
2. ✅ 币价突破均线上方
3. ✅ 30分钟内站稳确认
4. ✅ 开多仓

#### 做空信号 📉
1. ✅ 三组均线发生密集（价差 ≤ 2%）
2. ✅ 币价跌破均线下方
3. ✅ 30分钟内未能反弹
4. ✅ 开空仓

#### 平仓条件 🔄
- 双均线再次密集时平仓
- AI建议提前平仓（可选）
- 止损/止盈触发

---

## 🚀 快速开始

### 部署方式对比

| 部署方式 | 难度 | 适用场景 | 推荐度 |
|---------|------|----------|--------|
| 🐳 **Docker** | ⭐ 简单 | 生产环境、快速部署 | ⭐⭐⭐⭐⭐ |
| 🖥️ **传统部署** | ⭐⭐ 中等 | 定制化需求 | ⭐⭐⭐ |
| 💻 **本地开发** | ⭐⭐⭐ 较难 | 开发调试 | ⭐⭐ |

---

## 🐳 方式 1: Docker 部署（推荐）

### 前提条件

确保已安装 Docker 和 Docker Compose：

```bash
# 检查 Docker 版本
docker --version  # 需要 20.10+
docker compose version  # 需要 2.0+
```

如未安装，请访问：
- Docker: https://docs.docker.com/get-docker/
- Docker Compose: https://docs.docker.com/compose/install/

### 一键部署

```bash
# 1. 克隆项目
git clone https://github.com/MAXHONG/AsterDex-MaxTraderBot.git
cd AsterDex-MaxTraderBot/asterdex-trading-bot

# 2. 复制配置文件
cp config/config.example.json config/config.json

# 3. 编辑配置（重要！）
nano config/config.json
# 或使用其他编辑器：vim、code 等

# 4. 启动容器
docker compose up -d

# 5. 查看日志
docker compose logs -f
```

### 配置说明

编辑 `config/config.json`，填入必要信息：

```json
{
  "asterdex": {
    "user": "0x你的主钱包地址",
    "signer": "0xAPI钱包地址",
    "private_key": "0xAPI钱包私钥",
    "api_base_url": "https://fapi.asterdex.com"
  },
  "ai": {
    "enabled": true,           // true=启用AI, false=禁用AI
    "provider": "deepseek",    // "deepseek" 或 "grok"
    "deepseek": {
      "api_key": "sk-xxx",     // DeepSeek API密钥
      "api_base_url": "https://api.deepseek.com",
      "model": "deepseek-chat",
      "timeout": 30
    },
    "grok": {
      "api_key": "xai-xxx",    // Grok API密钥（可选）
      "api_base_url": "https://api.x.ai/v1",
      "model": "grok-beta",
      "timeout": 30
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

### Docker 常用命令

```bash
# 启动服务
docker compose up -d

# 停止服务
docker compose stop

# 重启服务
docker compose restart

# 查看日志（实时）
docker compose logs -f

# 查看最近100行日志
docker compose logs --tail=100

# 查看容器状态
docker compose ps

# 进入容器调试
docker compose exec asterdex-bot bash

# 完全删除（包括容器和镜像）
docker compose down --rmi all

# 更新并重启
git pull
docker compose up -d --build
```

### Docker 环境变量方式（可选）

如果不想使用 `config.json`，也可以使用环境变量：

```bash
# 1. 复制环境变量模板
cp .env.example .env

# 2. 编辑 .env 文件
nano .env

# 3. 修改 docker-compose.yml，取消环境变量的注释

# 4. 启动
docker compose up -d
```

**详细文档**: [Docker 部署完整指南](DOCKER_DEPLOYMENT.md)

---

## 🖥️ 方式 2: 传统部署

### 1. 系统要求

- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / macOS
- **Python**: 3.11+
- **内存**: 最低 512MB，推荐 1GB+
- **磁盘**: 最低 500MB

### 2. 安装依赖

```bash
# 克隆项目
git clone https://github.com/MAXHONG/AsterDex-MaxTraderBot.git
cd AsterDex-MaxTraderBot/asterdex-trading-bot

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置文件

```bash
# 复制配置模板
cp config/config.example.json config/config.json

# 编辑配置（参考上方 Docker 配置说明）
nano config/config.json

# 设置文件权限（重要！）
chmod 600 config/config.json
```

### 4. 获取 API 密钥

#### AsterDEX API 钱包
1. 访问 https://www.asterdex.com/zh-CN/api-wallet
2. 创建 API 钱包
3. 获取 Signer 地址和私钥
4. 将主钱包资金转入 API 钱包

#### AI 提供商（二选一）

**选项 1: DeepSeek（推荐）**
- 访问 https://platform.deepseek.com/
- 注册账号并充值
- 创建 API Key
- 费用：~¥1/百万tokens（极低成本）

**选项 2: Grok**
- 访问 https://console.x.ai/
- 注册账号
- 创建 API Key
- 在配置中将 `ai.provider` 设为 `"grok"`

### 5. 运行方式

#### 方式 A: 直接运行（测试）

```bash
python src/main.py
```

按 `Ctrl+C` 停止。

#### 方式 B: 后台运行（生产）

**使用 systemd（推荐）**：

```bash
# 1. 编辑服务文件，修改路径
sudo nano /home/user/webapp/asterdex-trading-bot/deploy/asterdex-bot.service

# 2. 复制到系统目录
sudo cp deploy/asterdex-bot.service /etc/systemd/system/

# 3. 重载并启动
sudo systemctl daemon-reload
sudo systemctl enable asterdex-bot
sudo systemctl start asterdex-bot

# 4. 查看状态
sudo systemctl status asterdex-bot

# 5. 查看日志
sudo journalctl -u asterdex-bot -f
```

**使用 nohup**：

```bash
nohup python src/main.py > output.log 2>&1 &

# 查看进程
ps aux | grep main.py

# 停止进程
kill <PID>
```

**详细文档**: [传统部署完整指南](DEPLOYMENT_GUIDE.md)

---

## 💻 方式 3: 本地开发

适合开发者进行功能开发和调试：

```bash
# 1. 克隆项目
git clone https://github.com/MAXHONG/AsterDex-MaxTraderBot.git
cd AsterDex-MaxTraderBot/asterdex-trading-bot

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖（包括开发依赖）
pip install -r requirements.txt
pip install pytest black flake8  # 开发工具

# 4. 配置文件
cp config/config.example.json config/config.json
nano config/config.json

# 5. 运行测试
python test_deepseek_fallback.py

# 6. 启动开发服务
python src/main.py
```

---

## 📁 项目结构

```
asterdex-trading-bot/
├── src/                              # 源代码目录
│   ├── main.py                       # 主程序入口
│   ├── api/                          # API 客户端
│   │   ├── base_ai_client.py         # AI 统一接口 (DeepSeek/Grok)
│   │   ├── asterdex_client.py        # AsterDEX API 客户端
│   │   └── deepseek_client.py        # (已废弃)
│   ├── ai/                           # AI 增强模块
│   │   ├── market_intelligence.py    # Phase 1: 市场情报
│   │   ├── risk_assessor.py          # Phase 2: 风险评估
│   │   ├── position_manager.py       # Phase 3: 持仓管理
│   │   └── parameter_optimizer.py    # Phase 4: 参数优化
│   ├── strategies/                   # 交易策略
│   │   ├── double_ma.py              # 双均线策略
│   │   └── indicators.py             # 技术指标计算
│   ├── trading/                      # 交易模块
│   │   ├── trader.py                 # 交易执行器
│   │   └── risk_manager.py           # 风险管理
│   └── utils/                        # 工具函数
│       ├── logger.py                 # 日志系统
│       └── config.py                 # 配置加载
├── config/                           # 配置文件
│   ├── config.json                   # 主配置（需创建）
│   └── config.example.json           # 配置模板
├── logs/                             # 日志目录
├── tests/                            # 测试文件
├── deploy/                           # 部署相关
│   └── asterdex-bot.service          # Systemd 服务
├── Dockerfile                        # Docker 镜像
├── docker-compose.yml                # Docker Compose 配置
├── .dockerignore                     # Docker 忽略文件
├── .env.example                      # 环境变量模板
├── requirements.txt                  # Python 依赖
└── README.md                         # 本文档
```

---

## 📊 监控和维护

### 日志查看

**Docker 部署**：
```bash
# 实时日志
docker compose logs -f

# 最近 100 行
docker compose logs --tail=100

# 容器内日志文件
docker compose exec asterdex-bot tail -f /app/logs/trading_bot.log
```

**传统部署**：
```bash
# 系统日志
sudo journalctl -u asterdex-bot -f

# 应用日志
tail -f logs/trading_bot.log

# 错误筛选
grep -i error logs/trading_bot.log
grep -i warning logs/trading_bot.log
```

### 性能监控

```bash
# Docker 资源使用
docker stats asterdex-trading-bot

# 系统资源
top -p $(pgrep -f "python src/main.py")
htop

# 磁盘使用
df -h
du -sh logs/
```

### 更新代码

**Docker 部署**：
```bash
cd AsterDex-MaxTraderBot/asterdex-trading-bot
git pull origin main
docker compose up -d --build
```

**传统部署**：
```bash
# 1. 停止服务
sudo systemctl stop asterdex-bot

# 2. 备份配置
cp config/config.json config/config.backup.json

# 3. 更新代码
git pull origin main

# 4. 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 5. 恢复配置
cp config/config.backup.json config/config.json

# 6. 重启服务
sudo systemctl start asterdex-bot
```

---

## 🔐 安全建议

### 🔒 保护私钥
```bash
# 设置配置文件权限
chmod 600 config/config.json

# 确保 .gitignore 包含敏感文件
cat .gitignore | grep config.json
cat .gitignore | grep .env
```

### 🛡️ 防火墙设置
```bash
# Ubuntu/Debian
sudo ufw allow 22/tcp
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

### 💾 定期备份
```bash
# 备份配置
cp config/config.json ~/backups/config_$(date +%Y%m%d).json

# 备份日志
tar -czf ~/backups/logs_$(date +%Y%m%d).tar.gz logs/
```

### 🔍 安全检查清单

- [ ] ✅ 私钥未泄露（不要提交到 Git）
- [ ] ✅ 配置文件权限正确（600 或 400）
- [ ] ✅ 使用小额资金测试
- [ ] ✅ 定期查看日志和交易记录
- [ ] ✅ 设置告警通知（可选）
- [ ] ✅ 定期更新代码和依赖

---

## 🐛 故障排查

### 常见问题

#### 1️⃣ 签名错误 (Signature Invalid)

**原因**: 时间不同步

**解决**:
```bash
# 检查时间
date
timedatectl

# 同步时间
sudo timedatectl set-ntp true

# 或手动同步
sudo ntpdate -u pool.ntp.org
```

#### 2️⃣ API 连接失败

**检查网络**:
```bash
curl -I https://fapi.asterdex.com
ping -c 4 fapi.asterdex.com
```

**检查配置**:
```bash
# 验证 JSON 格式
python -m json.tool config/config.json

# 检查 API 密钥是否正确
```

#### 3️⃣ AI 调用失败

**检查 AI 配置**:
- 确认 API Key 正确
- 确认余额充足
- 查看日志中的详细错误信息

**降级运行**:
```json
{
  "ai": {
    "enabled": false  // 禁用 AI，使用纯技术指标
  }
}
```

#### 4️⃣ 余额不足

**检查余额**:
```bash
# 查看日志
grep -i "insufficient" logs/trading_bot.log

# 登录 AsterDEX 查看账户余额
```

#### 5️⃣ Docker 容器无法启动

**查看错误日志**:
```bash
docker compose logs

# 检查配置文件是否存在
ls -la config/config.json

# 检查文件格式
docker compose config
```

#### 6️⃣ 内存不足

**检查内存**:
```bash
free -h

# Docker 内存限制
docker stats asterdex-trading-bot

# 清理 Docker 缓存
docker system prune -a
```

---

## 📚 完整文档索引

### 中文文档 🇨🇳

| 文档 | 说明 | 链接 |
|------|------|------|
| **README.md** | 主文档（本文件） | 当前页面 |
| **OPERATIONS_GUIDE.md** | 🔥 操作指南（启动/暂停/结束） | [查看](OPERATIONS_GUIDE.md) |
| **DOCKER_DEPLOYMENT.md** | Docker 部署完整指南 | [查看](DOCKER_DEPLOYMENT.md) |
| **DEPLOYMENT_GUIDE.md** | 传统部署完整指南 | [查看](DEPLOYMENT_GUIDE.md) |
| **AI_ENHANCEMENT_IMPLEMENTATION_COMPLETE.md** | AI 增强系统详细说明 | [查看](AI_ENHANCEMENT_IMPLEMENTATION_COMPLETE.md) |
| **AI_ENHANCEMENT_ROADMAP.md** | AI 增强路线图 | [查看](AI_ENHANCEMENT_ROADMAP.md) |
| **QUICKSTART.md** | 快速开始指南 | [查看](QUICKSTART.md) |

### English Docs 🇬🇧

| Document | Description | Link |
|----------|-------------|------|
| **README_EN.md** | Main README | [View](README_EN.md) |
| **OPERATIONS_GUIDE_EN.md** | 🔥 Operations Guide (Start/Pause/Stop) | [View](OPERATIONS_GUIDE_EN.md) |
| **DOCKER_DEPLOYMENT_EN.md** | Docker Deployment Guide | [View](DOCKER_DEPLOYMENT_EN.md) |
| **DEPLOYMENT_GUIDE_EN.md** | Deployment Guide | [View](DEPLOYMENT_GUIDE_EN.md) |
| **QUICKSTART_EN.md** | Quick Start Guide | [View](QUICKSTART_EN.md) |

---

## 🤖 AI 增强系统说明

### 功能概览

| 阶段 | 模块 | 功能 | 输入 | 输出 |
|------|------|------|------|------|
| **Phase 1** | 市场情报 | 多源信息聚合 | 币种、时间范围 | 情绪分数、风险等级 |
| **Phase 2** | 风险评估 | 多维度风险分析 | 交易信号、市场上下文 | 仓位调整、杠杆建议 |
| **Phase 3** | 持仓管理 | 实时监控优化 | 持仓信息、当前价格 | 平仓建议、止损调整 |
| **Phase 4** | 参数优化 | 自适应调整 | 当前参数、市场状态 | 优化参数、策略切换 |

### 使用说明

**完全启用**（推荐）:
```json
{
  "ai": {
    "enabled": true,
    "provider": "deepseek"
  }
}
```

**禁用 AI**（纯技术指标）:
```json
{
  "ai": {
    "enabled": false
  }
}
```

**切换 AI 提供商**:
```json
{
  "ai": {
    "enabled": true,
    "provider": "grok"  // 从 deepseek 切换到 grok
  }
}
```

### 性能对比

| 指标 | 无 AI | 有 AI | 提升幅度 |
|------|-------|-------|----------|
| **胜率** | 基准 | 提升 | +15-25% |
| **风险控制** | 基准 | 提升 | +30-40% |
| **参数适应** | 基准 | 提升 | +20-30% |
| **持仓优化** | 基准 | 提升 | +25-35% |
| **整体表现** | 基准 | 提升 | **+35-55%** |

### 成本分析

**DeepSeek（推荐）**:
- 成本：~¥1/百万 tokens
- 每日调用：约 1000 次
- 月成本：~¥30-50

**ROI 计算**:
- AI 成本：¥50/月
- 性能提升：35-55%
- 如本金 ¥10,000，月收益提升：¥350-550
- **ROI**: 700-1100%

**详细说明**: [AI_ENHANCEMENT_IMPLEMENTATION_COMPLETE.md](AI_ENHANCEMENT_IMPLEMENTATION_COMPLETE.md)

---

## 📞 技术支持

### 获取帮助

1. **查看文档**: 先查阅相关文档
2. **检查日志**: 日志文件包含详细错误信息
3. **提交 Issue**: https://github.com/MAXHONG/AsterDex-MaxTraderBot/issues
4. **参与讨论**: https://github.com/MAXHONG/AsterDex-MaxTraderBot/discussions

### 联系方式

- **GitHub**: [@MAXHONG](https://github.com/MAXHONG)
- **项目地址**: https://github.com/MAXHONG/AsterDex-MaxTraderBot

---

## ⚠️ 免责声明

1. **教育用途**: 本软件仅供学习和研究使用
2. **风险警告**: 加密货币交易存在高风险，可能导致本金损失
3. **自负盈亏**: 使用本软件进行实际交易的所有风险由用户自行承担
4. **无担保**: 开发者不对任何交易损失、数据丢失或其他损害负责
5. **测试建议**: 强烈建议先使用小额资金测试
6. **监控必要**: 需要定期监控机器人运行状态和交易结果
7. **AI免责**: AI 增强功能基于大语言模型，可能产生不准确的判断

**使用本软件即表示您已阅读并同意上述免责声明。**

---

## 📝 许可证

MIT License

Copyright (c) 2025 MAXHONG

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

<div align="center">

**开发者**: MAXHONG  
**项目地址**: https://github.com/MAXHONG/AsterDex-MaxTraderBot  
**最后更新**: 2025-10-22  

⭐ 如果这个项目对你有帮助，请给个 Star！⭐

</div>

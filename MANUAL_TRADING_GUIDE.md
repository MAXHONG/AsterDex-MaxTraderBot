# 手动交易功能使用指南

**完整的手动下单 + 自动平仓系统**

---

## 🎯 功能概述

手动交易功能允许您**手动发送交易指令立即开仓**，然后机器人会**自动监控并在合适时机平仓**。

### 核心特性

- ✅ **手动开仓**：通过 API/文件发送指令，立即执行开仓
- ✅ **自动平仓**：机器人监控持仓，根据策略自动平仓
- ✅ **止损止盈**：支持设置止损/止盈百分比
- ✅ **多种接入方式**：HTTP API、文件监听
- ✅ **独立监控**：手动持仓独立管理，不影响自动交易策略

---

## 🚀 快速开始

### 1. 启用手动交易功能

编辑 `config/config.json`：

```json
{
  "manual_trading": {
    "enabled": true,
    "api_server": {
      "enabled": true,
      "host": "0.0.0.0",
      "port": 8080
    },
    "file_watch": {
      "enabled": true,
      "order_file": "manual_orders.json"
    },
    "default_leverage": 3,
    "default_position_percent": 20,
    "check_interval": 10
  }
}
```

### 2. 启动机器人

```bash
# Docker 部署
docker compose up -d

# 传统部署
python src/main.py
```

### 3. 验证 API 服务

```bash
curl http://localhost:8080/health
```

---

## 📡 方式 1: HTTP API

### 创建做多订单

```bash
curl -X POST http://localhost:8080/order \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "side": "LONG",
    "leverage": 3,
    "stop_loss_percent": 2.0,
    "take_profit_percent": 5.0,
    "note": "手动做多BTC"
  }'
```

### 创建做空订单

```bash
curl -X POST http://localhost:8080/order \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "ETHUSDT",
    "side": "SHORT",
    "leverage": 2,
    "stop_loss_percent": 3.0,
    "take_profit_percent": 6.0,
    "note": "手动做空ETH"
  }'
```

### 查看所有手动持仓

```bash
curl http://localhost:8080/positions
```

### 手动关闭持仓

```bash
curl -X POST http://localhost:8080/close/{order_id}
```

---

## 📄 方式 2: 文件监听

创建 `manual_orders.json`：

```json
{
  "symbol": "BNBUSDT",
  "side": "LONG",
  "leverage": 3,
  "stop_loss_percent": 2.5,
  "take_profit_percent": 7.0,
  "note": "通过文件下单"
}
```

机器人会自动检测文件变化并执行订单。

---

## 📊 参数说明

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `symbol` | ✅ | 交易对 | "BTCUSDT", "ETHUSDT" |
| `side` | ✅ | 方向 | "LONG"=做多, "SHORT"=做空 |
| `quantity` | ❌ | 数量 | 0.1（不填使用默认仓位） |
| `leverage` | ❌ | 杠杆 | 3（不填使用配置的杠杆） |
| `stop_loss_percent` | ❌ | 止损百分比 | 2.0 表示 2% |
| `take_profit_percent` | ❌ | 止盈百分比 | 5.0 表示 5% |
| `note` | ❌ | 备注 | "手动下单" |

---

## 🔄 自动平仓机制

机器人会持续监控手动开仓的持仓，并在以下情况自动平仓：

### 1. 触发止损

- **做多**：当前价 ≤ 开仓价 × (1 - 止损%)
- **做空**：当前价 ≥ 开仓价 × (1 + 止损%)

### 2. 触发止盈

- **做多**：当前价 ≥ 开仓价 × (1 + 止盈%)
- **做空**：当前价 ≤ 开仓价 × (1 - 止盈%)

### 3. 策略判断（可选）

如果启用 AI 增强，AI 会根据市场行情建议平仓。

---

## 📈 使用场景

### 场景 1: 突发行情快速进场

当看到突发利好/利空消息时：

```bash
# 快速做多
curl -X POST http://localhost:8080/order \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT","side":"LONG","leverage":5,"stop_loss_percent":1.5,"take_profit_percent":3.0}'
```

机器人立即开仓，然后自动监控并在合适时机平仓。

### 场景 2: 定向加仓

当自动策略已有持仓，想手动加仓：

```bash
# 加仓做多
curl -X POST http://localhost:8080/order \
  -H "Content-Type: application/json" \
  -d '{"symbol":"ETHUSDT","side":"LONG","quantity":0.5,"note":"手动加仓"}'
```

### 场景 3: 对冲操作

当想对冲风险时：

```bash
# 开反向仓位
curl -X POST http://localhost:8080/order \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT","side":"SHORT","leverage":3,"note":"对冲"}'
```

---

## 🖥️ API 文档

访问 http://localhost:8080/ 查看完整 API 文档。

### API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/positions` | 获取所有手动持仓 |
| POST | `/order` | 创建手动交易指令 |
| POST | `/close/{order_id}` | 关闭指定持仓 |

---

## 🧪 测试

运行测试脚本：

```bash
python test_manual_order.py
```

或手动测试：

```bash
# 1. 健康检查
curl http://localhost:8080/health

# 2. 查看持仓
curl http://localhost:8080/positions

# 3. 创建测试订单（使用测试金额）
curl -X POST http://localhost:8080/order \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT","side":"LONG","quantity":0.001,"stop_loss_percent":1.0,"take_profit_percent":2.0,"note":"测试"}'
```

---

## ⚙️ 配置详解

### 默认仓位大小

```json
"default_position_percent": 20  // 使用可用余额的 20%
```

### 默认杠杆

```json
"default_leverage": 3  // 默认 3 倍杠杆
```

### 监控间隔

```json
"check_interval": 10  // 每 10 秒检查一次持仓
```

### API 服务器配置

```json
"api_server": {
  "enabled": true,
  "host": "0.0.0.0",  // 监听所有网络接口
  "port": 8080        // 端口号
}
```

### 文件监听配置

```json
"file_watch": {
  "enabled": true,
  "order_file": "manual_orders.json"  // 指令文件路径
}
```

---

## 🔐 安全建议

1. **限制 API 访问**：
   - 生产环境建议设置 `host: "127.0.0.1"` 仅允许本地访问
   - 使用防火墙限制端口访问

2. **小额测试**：
   - 先用小额资金测试手动交易功能
   - 确认止损止盈正常工作

3. **监控日志**：
   - 定期查看日志文件
   - 关注开仓和平仓记录

4. **设置止损**：
   - 手动订单务必设置止损
   - 止损百分比建议 1-3%

---

## 📝 日志查看

### Docker 部署

```bash
docker compose logs -f | grep "手动"
```

### 传统部署

```bash
tail -f logs/trading_bot.log | grep "手动"
```

### 查看手动持仓日志

```bash
grep "手动交易\|自动平仓" logs/trading_bot.log
```

---

## ⚠️ 重要提醒

1. **立即开仓**：收到指令后立即执行，无需等待策略信号
2. **自动平仓**：机器人会持续监控并自动平仓，无需手动干预
3. **独立管理**：手动持仓与自动策略持仓独立管理
4. **止损必设**：强烈建议设置止损百分比
5. **实时监控**：机器人停止运行时不会监控手动持仓

---

## 🐛 故障排查

### API 无法访问

```bash
# 检查端口
netstat -tulpn | grep 8080

# 检查机器人日志
tail -100 logs/trading_bot.log
```

### 手动订单未执行

1. 检查配置文件 `manual_trading.enabled` 是否为 `true`
2. 检查机器人是否正在运行
3. 查看日志获取详细错误信息

### 自动平仓未触发

1. 检查持仓是否已设置止损/止盈
2. 确认机器人正在运行
3. 查看监控线程日志

---

## 📞 获取帮助

- 查看日志：`logs/trading_bot.log`
- API 文档：http://localhost:8080/
- 测试脚本：`python test_manual_order.py`
- 提交 Issue：https://github.com/MAXHONG/AsterDex-MaxTraderBot/issues

---

## 🎉 使用示例

### Python 示例

```python
import requests

# 创建手动订单
response = requests.post('http://localhost:8080/order', json={
    'symbol': 'BTCUSDT',
    'side': 'LONG',
    'leverage': 3,
    'stop_loss_percent': 2.0,
    'take_profit_percent': 5.0,
    'note': 'Python 手动下单'
})

result = response.json()
print(f"订单ID: {result['order_id']}")

# 查看持仓
positions = requests.get('http://localhost:8080/positions').json()
print(f"当前持仓数: {positions['count']}")
```

### JavaScript 示例

```javascript
// 创建手动订单
fetch('http://localhost:8080/order', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    symbol: 'ETHUSDT',
    side: 'SHORT',
    leverage: 2,
    stop_loss_percent: 3.0,
    take_profit_percent: 6.0,
    note: 'JS 手动下单'
  })
})
.then(res => res.json())
.then(data => console.log('订单ID:', data.order_id));
```

---

**最后更新**: 2025-10-22  
**文档版本**: v1.0

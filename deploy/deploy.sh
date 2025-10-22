#!/bin/bash
# AsterDEX 交易机器人部署脚本

set -e

echo "======================================"
echo "AsterDEX 交易机器人部署"
echo "======================================"

# 获取当前目录
CURRENT_DIR=$(pwd)
PROJECT_DIR=$(dirname "$CURRENT_DIR")

# 获取当前用户
CURRENT_USER=$(whoami)

echo "项目目录: $PROJECT_DIR"
echo "当前用户: $CURRENT_USER"

# 检查配置文件
if [ ! -f "$PROJECT_DIR/config/config.json" ]; then
    echo "错误: 配置文件不存在，请先创建 config/config.json"
    echo "可以从模板复制: cp config/config.example.json config/config.json"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "错误: 虚拟环境不存在，请先运行 deploy/install.sh"
    exit 1
fi

# 创建 systemd 服务文件
echo "创建 systemd 服务文件..."
SERVICE_FILE="/tmp/asterdex-bot.service"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=AsterDEX Trading Bot
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin:\$PATH"
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/src/main.py
Restart=on-failure
RestartSec=10s

# 日志
StandardOutput=journal
StandardError=journal
SyslogIdentifier=asterdex-bot

# 安全设置
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

echo "服务文件已创建: $SERVICE_FILE"

# 安装服务
echo ""
echo "安装系统服务需要 sudo 权限..."
echo "请输入 sudo 密码："

sudo cp "$SERVICE_FILE" /etc/systemd/system/asterdex-bot.service
sudo systemctl daemon-reload

echo ""
echo "======================================"
echo "部署完成！"
echo "======================================"
echo ""
echo "服务管理命令："
echo ""
echo "启动服务:"
echo "  sudo systemctl start asterdex-bot"
echo ""
echo "停止服务:"
echo "  sudo systemctl stop asterdex-bot"
echo ""
echo "重启服务:"
echo "  sudo systemctl restart asterdex-bot"
echo ""
echo "查看状态:"
echo "  sudo systemctl status asterdex-bot"
echo ""
echo "查看日志:"
echo "  sudo journalctl -u asterdex-bot -f"
echo ""
echo "开机自启:"
echo "  sudo systemctl enable asterdex-bot"
echo ""
echo "取消开机自启:"
echo "  sudo systemctl disable asterdex-bot"
echo ""

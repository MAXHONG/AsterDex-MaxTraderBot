#!/bin/bash
# AsterDEX 交易机器人安装脚本

set -e

echo "======================================"
echo "AsterDEX 交易机器人安装"
echo "======================================"

# 检查 Python 版本
echo "检查 Python 版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "错误: 需要 Python 3.9 或更高版本，当前版本: $python_version"
    exit 1
fi

echo "Python 版本检查通过: $python_version"

# 创建虚拟环境
echo "创建 Python 虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 升级 pip
echo "升级 pip..."
pip install --upgrade pip

# 安装依赖
echo "安装依赖包..."
pip install -r requirements.txt

echo ""
echo "======================================"
echo "安装完成！"
echo "======================================"
echo ""
echo "接下来的步骤："
echo "1. 复制配置文件模板："
echo "   cp config/config.example.json config/config.json"
echo ""
echo "2. 编辑配置文件："
echo "   vim config/config.json"
echo "   或"
echo "   nano config/config.json"
echo ""
echo "3. 填写以下信息："
echo "   - AsterDEX 主钱包地址"
echo "   - AsterDEX API 钱包地址和私钥"
echo "   - DeepSeek API 密钥（可选）"
echo "   - 交易参数（杠杆、币种等）"
echo ""
echo "4. 测试运行："
echo "   source venv/bin/activate"
echo "   python src/main.py"
echo ""
echo "5. 部署为系统服务（可选）："
echo "   bash deploy/deploy.sh"
echo ""

#!/usr/bin/env python3
"""测试导入所有模块"""
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("测试导入模块...")

try:
    from utils import Config, get_config, setup_logger, get_logger
    print("✅ utils 模块导入成功")
    
    from api import AsterDexClient, DeepSeekClient
    print("✅ api 模块导入成功")
    
    from strategies import TechnicalIndicators, DoubleMaStrategy
    print("✅ strategies 模块导入成功")
    
    from trading import Trader, RiskManager
    print("✅ trading 模块导入成功")
    
    print("\n所有模块导入成功！✅")
    print("\n项目结构正确，可以进行部署。")
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

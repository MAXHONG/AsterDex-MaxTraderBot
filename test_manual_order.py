#!/usr/bin/env python3
"""
手动交易功能测试脚本
"""
import requests
import json
import time


def test_api_health():
    """测试 API 健康状态"""
    print("=" * 60)
    print("1. 测试 API 健康状态")
    print("=" * 60)
    
    try:
        response = requests.get('http://localhost:8080/health')
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_get_positions():
    """测试获取持仓列表"""
    print("\n" + "=" * 60)
    print("2. 测试获取持仓列表")
    print("=" * 60)
    
    try:
        response = requests.get('http://localhost:8080/positions')
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_create_long_order():
    """测试创建做多订单"""
    print("\n" + "=" * 60)
    print("3. 测试创建做多订单（模拟）")
    print("=" * 60)
    
    order_data = {
        "symbol": "BTCUSDT",
        "side": "LONG",
        "quantity": None,  # 使用默认仓位大小
        "leverage": 3,
        "stop_loss_percent": 2.0,
        "take_profit_percent": 5.0,
        "note": "测试做多订单"
    }
    
    print(f"订单参数: {json.dumps(order_data, indent=2, ensure_ascii=False)}")
    print("\n⚠️  这是模拟测试，实际不会创建订单")
    print("如需真实测试，请取消下方注释并确保机器人正在运行\n")
    
    # 取消注释以执行真实测试
    # try:
    #     response = requests.post(
    #         'http://localhost:8080/order',
    #         json=order_data,
    #         headers={'Content-Type': 'application/json'}
    #     )
    #     print(f"状态码: {response.status_code}")
    #     print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    #     return response.json().get('order_id')
    # except Exception as e:
    #     print(f"❌ 错误: {e}")
    #     return None
    
    return None


def test_create_short_order():
    """测试创建做空订单"""
    print("\n" + "=" * 60)
    print("4. 测试创建做空订单（模拟）")
    print("=" * 60)
    
    order_data = {
        "symbol": "ETHUSDT",
        "side": "SHORT",
        "leverage": 2,
        "stop_loss_percent": 3.0,
        "take_profit_percent": 6.0,
        "note": "测试做空订单"
    }
    
    print(f"订单参数: {json.dumps(order_data, indent=2, ensure_ascii=False)}")
    print("\n⚠️  这是模拟测试，实际不会创建订单")
    
    return None


def test_close_position(order_id: str):
    """测试关闭持仓"""
    if not order_id:
        print("\n跳过关闭持仓测试（无订单ID）")
        return
    
    print("\n" + "=" * 60)
    print(f"5. 测试关闭持仓 {order_id}（模拟）")
    print("=" * 60)
    
    # 取消注释以执行真实测试
    # try:
    #     response = requests.post(f'http://localhost:8080/close/{order_id}')
    #     print(f"状态码: {response.status_code}")
    #     print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    # except Exception as e:
    #     print(f"❌ 错误: {e}")


def test_file_order():
    """测试文件方式下单"""
    print("\n" + "=" * 60)
    print("6. 测试文件方式下单（模拟）")
    print("=" * 60)
    
    order_data = {
        "symbol": "BNBUSDT",
        "side": "LONG",
        "leverage": 3,
        "stop_loss_percent": 2.5,
        "take_profit_percent": 7.0,
        "note": "通过文件下单",
        "processed": False
    }
    
    print("创建订单文件 manual_orders.json")
    print(f"内容: {json.dumps(order_data, indent=2, ensure_ascii=False)}")
    print("\n⚠️  如需真实测试，请执行以下命令：")
    print("echo '" + json.dumps(order_data) + "' > manual_orders.json")


def main():
    """主测试函数"""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║         AsterDEX 手动交易功能测试脚本                    ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print("\n⚠️  重要提示：")
    print("1. 确保交易机器人正在运行")
    print("2. 确保手动交易功能已启用（config.json manual_trading.enabled = true）")
    print("3. 本脚本默认只进行模拟测试，不会实际下单")
    print("4. 如需真实测试，请编辑脚本并取消相关注释\n")
    
    input("按 Enter 键继续...")
    
    # 测试 API 健康状态
    if not test_api_health():
        print("\n❌ API 服务器未运行，请先启动机器人")
        return
    
    # 测试获取持仓
    test_get_positions()
    
    # 测试创建订单
    order_id = test_create_long_order()
    test_create_short_order()
    
    # 测试关闭持仓
    test_close_position(order_id)
    
    # 测试文件下单
    test_file_order()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
    print("\n📚 使用文档: MANUAL_TRADING_GUIDE.md")
    print("🌐 API 文档: http://localhost:8080/\n")


if __name__ == '__main__':
    main()

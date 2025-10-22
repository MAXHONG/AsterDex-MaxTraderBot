#!/usr/bin/env python3
"""
测试 DeepSeek 可选功能和兜底逻辑

这个脚本验证：
1. 没有 DeepSeek 配置时，机器人可以正常运行
2. DeepSeek API 失败时，机器人使用本地策略继续交易
3. DeepSeek 可用时，可以正常提供辅助决策
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.trading.trader import Trader
from src.api import DeepSeekClient
from unittest.mock import Mock, MagicMock
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def create_mock_trader(with_deepseek=False, deepseek_fails=False):
    """创建模拟的交易器"""
    
    # 模拟 AsterDEX 客户端
    mock_asterdex = Mock()
    mock_asterdex.get_balance.return_value = [
        {'asset': 'USDT', 'availableBalance': '10000.0'}
    ]
    mock_asterdex.get_position_info.return_value = []
    mock_asterdex.get_ticker_price.return_value = {'price': '50000.0'}
    mock_asterdex.get_exchange_info.return_value = {
        'symbols': [{
            'symbol': 'BTCUSDT',
            'filters': [
                {'filterType': 'LOT_SIZE', 'minQty': '0.001', 'stepSize': '0.001'},
                {'filterType': 'PRICE_FILTER', 'minPrice': '0.01', 'tickSize': '0.01'}
            ]
        }]
    }
    mock_asterdex.ping.return_value = {}
    
    # 模拟 DeepSeek 客户端
    mock_deepseek = None
    if with_deepseek:
        mock_deepseek = Mock(spec=DeepSeekClient)
        if deepseek_fails:
            # 模拟 API 失败
            mock_deepseek.analyze_trading_signal.side_effect = Exception("API 连接失败")
            mock_deepseek.get_market_sentiment.side_effect = Exception("API 连接失败")
        else:
            # 模拟正常返回
            mock_deepseek.get_market_sentiment.return_value = {
                'analysis': '市场情绪积极'
            }
            mock_deepseek.analyze_trading_signal.return_value = {
                'action': 'BUY',
                'confidence': 80,
                'reason': 'AI 建议买入'
            }
    
    # 模拟风险管理器
    mock_risk_manager = Mock()
    mock_risk_manager.check_position_risk.return_value = {
        'risk_level': 'LOW',
        'margin_usage_percent': 10.0
    }
    mock_risk_manager.calculate_position_size.return_value = {
        'quantity': 0.01,
        'notional': 500.0,
        'margin': 100.0
    }
    mock_risk_manager.validate_order.return_value = (True, None)
    
    # 模拟策略
    mock_strategy = Mock()
    
    # 创建交易器
    trader = Trader(
        asterdex_client=mock_asterdex,
        deepseek_client=mock_deepseek,
        risk_manager=mock_risk_manager,
        strategy=mock_strategy,
        leverage=5
    )
    
    trader.exchange_info = mock_asterdex.get_exchange_info()
    
    return trader

def test_without_deepseek():
    """测试1: 没有 DeepSeek 时正常运行"""
    logger.info("\n" + "="*60)
    logger.info("测试1: 没有配置 DeepSeek")
    logger.info("="*60)
    
    trader = create_mock_trader(with_deepseek=False)
    
    # 模拟一个低置信度信号（通常会触发 AI 确认）
    signal = {
        'action': 'BUY',
        'confidence': 75,  # < 90，会触发 AI 确认
        'reason': '本地策略检测到买入信号',
        'current_price': 50000.0,
        'ma_data': {'sma20': 49000, 'sma60': 48000, 'sma120': 47000}
    }
    
    # 执行信号
    result = trader.execute_signal('BTCUSDT', signal, '15m')
    
    if result:
        logger.info("✓ 测试通过: 没有 DeepSeek 也能正常下单")
        return True
    else:
        logger.error("✗ 测试失败: 应该能正常下单")
        return False

def test_with_deepseek_failure():
    """测试2: DeepSeek 失败时使用本地策略"""
    logger.info("\n" + "="*60)
    logger.info("测试2: DeepSeek API 失败")
    logger.info("="*60)
    
    trader = create_mock_trader(with_deepseek=True, deepseek_fails=True)
    
    # 模拟一个低置信度信号
    signal = {
        'action': 'BUY',
        'confidence': 75,
        'reason': '本地策略检测到买入信号',
        'current_price': 50000.0,
        'ma_data': {'sma20': 49000, 'sma60': 48000, 'sma120': 47000}
    }
    
    # 执行信号
    result = trader.execute_signal('BTCUSDT', signal, '15m')
    
    if result:
        logger.info("✓ 测试通过: DeepSeek 失败后使用本地策略继续交易")
        return True
    else:
        logger.error("✗ 测试失败: 应该降级到本地策略继续")
        return False

def test_with_deepseek_success():
    """测试3: DeepSeek 正常工作"""
    logger.info("\n" + "="*60)
    logger.info("测试3: DeepSeek 正常运行")
    logger.info("="*60)
    
    trader = create_mock_trader(with_deepseek=True, deepseek_fails=False)
    
    # 模拟一个低置信度信号
    signal = {
        'action': 'BUY',
        'confidence': 75,
        'reason': '本地策略检测到买入信号',
        'current_price': 50000.0,
        'ma_data': {'sma20': 49000, 'sma60': 48000, 'sma120': 47000}
    }
    
    # 执行信号
    result = trader.execute_signal('BTCUSDT', signal, '15m')
    
    if result:
        logger.info("✓ 测试通过: DeepSeek 提供辅助决策，正常下单")
        return True
    else:
        logger.error("✗ 测试失败: DeepSeek 正常时应该能下单")
        return False

def test_high_confidence_skip_ai():
    """测试4: 高置信度信号跳过 AI 确认"""
    logger.info("\n" + "="*60)
    logger.info("测试4: 高置信度信号（>= 90）跳过 AI")
    logger.info("="*60)
    
    trader = create_mock_trader(with_deepseek=True, deepseek_fails=False)
    
    # 模拟一个高置信度信号
    signal = {
        'action': 'BUY',
        'confidence': 95,  # >= 90，不会触发 AI 确认
        'reason': '本地策略强烈看涨',
        'current_price': 50000.0,
        'ma_data': {'sma20': 49000, 'sma60': 48000, 'sma120': 47000}
    }
    
    # 执行信号
    result = trader.execute_signal('BTCUSDT', signal, '15m')
    
    # 验证没有调用 DeepSeek
    if result and not trader.deepseek.analyze_trading_signal.called:
        logger.info("✓ 测试通过: 高置信度信号直接交易，无需 AI 确认")
        return True
    else:
        logger.error("✗ 测试失败: 高置信度应该跳过 AI")
        return False

def main():
    """运行所有测试"""
    logger.info("\n" + "="*60)
    logger.info("DeepSeek 兜底逻辑测试套件")
    logger.info("="*60)
    
    tests = [
        test_without_deepseek,
        test_with_deepseek_failure,
        test_with_deepseek_success,
        test_high_confidence_skip_ai
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append((test_func.__name__, result))
        except Exception as e:
            logger.error(f"测试 {test_func.__name__} 异常: {e}")
            results.append((test_func.__name__, False))
    
    # 汇总结果
    logger.info("\n" + "="*60)
    logger.info("测试汇总")
    logger.info("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        logger.info(f"{status} - {test_name}")
    
    logger.info(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        logger.info("\n🎉 所有测试通过！DeepSeek 兜底逻辑工作正常")
        return 0
    else:
        logger.error(f"\n❌ {total - passed} 个测试失败")
        return 1

if __name__ == '__main__':
    sys.exit(main())

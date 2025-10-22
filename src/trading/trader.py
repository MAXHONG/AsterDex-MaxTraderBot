"""
交易执行器模块
"""
from typing import Dict, Any, Optional, List
import time

from ..api import AsterDexClient, DeepSeekClient
from ..strategies import DoubleMaStrategy
from .risk_manager import RiskManager
from ..utils.logger import get_logger


class Trader:
    """交易执行器"""
    
    def __init__(
        self,
        asterdex_client: AsterDexClient,
        deepseek_client: Optional[DeepSeekClient],
        risk_manager: RiskManager,
        strategy: DoubleMaStrategy,
        leverage: int = 5
    ):
        """
        初始化交易执行器
        
        Args:
            asterdex_client: AsterDEX 客户端
            deepseek_client: DeepSeek 客户端（可选）
            risk_manager: 风险管理器
            strategy: 交易策略
            leverage: 杠杆倍数
        """
        self.asterdex = asterdex_client
        self.deepseek = deepseek_client
        self.risk_manager = risk_manager
        self.strategy = strategy
        self.leverage = leverage
        self.logger = get_logger()
        
        # 缓存交易所信息
        self.exchange_info = None
        self.symbol_info_cache = {}
    
    def initialize(self):
        """初始化交易器"""
        try:
            # 获取交易所信息
            self.exchange_info = self.asterdex.get_exchange_info()
            self.logger.info("成功获取交易所信息")
            
            # 测试连接
            self.asterdex.ping()
            self.logger.info("AsterDEX API 连接正常")
            
        except Exception as e:
            self.logger.error(f"初始化失败: {e}")
            raise
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取交易对信息
        
        Args:
            symbol: 交易对符号
            
        Returns:
            交易对信息
        """
        if symbol in self.symbol_info_cache:
            return self.symbol_info_cache[symbol]
        
        if not self.exchange_info:
            return None
        
        symbols = self.exchange_info.get('symbols', [])
        for s in symbols:
            if s.get('symbol') == symbol:
                self.symbol_info_cache[symbol] = s
                return s
        
        return None
    
    def setup_symbol(self, symbol: str):
        """
        设置交易对（杠杆和保证金模式）
        
        Args:
            symbol: 交易对符号
        """
        try:
            # 设置杠杆
            self.logger.info(f"设置 {symbol} 杠杆为 {self.leverage}x")
            self.asterdex.change_leverage(symbol, self.leverage)
            
            # 设置保证金模式
            margin_type = self.risk_manager.margin_type
            self.logger.info(f"设置 {symbol} 保证金模式为 {margin_type}")
            try:
                self.asterdex.change_margin_type(symbol, margin_type)
            except Exception as e:
                # 如果已经是该模式，会报错，可以忽略
                self.logger.warning(f"设置保证金模式失败（可能已经是该模式）: {e}")
            
        except Exception as e:
            self.logger.error(f"设置 {symbol} 失败: {e}")
            raise
    
    def execute_signal(
        self,
        symbol: str,
        signal: Dict[str, Any],
        interval: str
    ) -> Optional[Dict[str, Any]]:
        """
        执行交易信号
        
        Args:
            symbol: 交易对符号
            signal: 交易信号
            interval: K线间隔
            
        Returns:
            订单信息
        """
        action = signal['action']
        
        if action == 'HOLD':
            return None
        
        try:
            # 获取账户余额
            balance_info = self.asterdex.get_balance()
            available_balance = self._get_available_balance(balance_info)
            
            self.logger.info(f"可用余额: {available_balance:.2f} USDT")
            
            # 获取当前持仓
            positions = self.asterdex.get_position_info(symbol)
            current_position = self._get_current_position(positions, symbol)
            
            # 检查风险
            risk_info = self.risk_manager.check_position_risk(
                positions,
                available_balance
            )
            self.logger.info(f"风险评估: {risk_info}")
            
            # 如果是平仓信号
            if action == 'CLOSE':
                if current_position and current_position['position_amt'] != 0:
                    return self._close_position(symbol, current_position)
                else:
                    self.logger.info(f"{symbol} 没有持仓，无需平仓")
                    return None
            
            # 如果是开仓信号
            elif action in ['BUY', 'SELL']:
                # 检查是否已有持仓
                if current_position and current_position['position_amt'] != 0:
                    self.logger.warning(f"{symbol} 已有持仓，跳过开仓信号")
                    return None
                
                # 检查风险等级
                if risk_info['risk_level'] == 'HIGH':
                    self.logger.warning(f"风险等级过高，跳过 {symbol} 开仓")
                    return None
                
                # 使用 DeepSeek 进行二次确认（如果配置了）
                if self.deepseek and signal['confidence'] < 90:
                    try:
                        ai_signal = self._get_ai_confirmation(symbol, signal)
                        if ai_signal['action'] == 'HOLD':
                            self.logger.info(f"AI 建议持有，跳过 {symbol} 开仓")
                            return None
                    except Exception as e:
                        self.logger.warning(f"AI 分析异常（使用本地策略继续）: {e}")
                
                # 执行开仓
                return self._open_position(symbol, action, available_balance, signal)
        
        except Exception as e:
            self.logger.error(f"执行信号失败 [{symbol}]: {e}")
            return None
    
    def _get_available_balance(self, balance_info: Dict[str, Any]) -> float:
        """
        获取可用余额
        
        Args:
            balance_info: 余额信息
            
        Returns:
            可用余额（USDT）
        """
        if isinstance(balance_info, list):
            for asset in balance_info:
                if asset.get('asset') == 'USDT':
                    return float(asset.get('availableBalance', 0))
        
        return 0.0
    
    def _get_current_position(
        self,
        positions: List[Dict[str, Any]],
        symbol: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取当前持仓
        
        Args:
            positions: 持仓列表
            symbol: 交易对符号
            
        Returns:
            持仓信息
        """
        for pos in positions:
            if pos.get('symbol') == symbol:
                position_amt = float(pos.get('positionAmt', 0))
                if position_amt != 0:
                    return {
                        'symbol': symbol,
                        'position_amt': position_amt,
                        'entry_price': float(pos.get('entryPrice', 0)),
                        'unrealized_profit': float(pos.get('unRealizedProfit', 0)),
                        'leverage': float(pos.get('leverage', 1)),
                        'position_side': pos.get('positionSide', 'BOTH')
                    }
        
        return None
    
    def _open_position(
        self,
        symbol: str,
        side: str,
        available_balance: float,
        signal: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        开仓
        
        Args:
            symbol: 交易对符号
            side: 买卖方向（BUY/SELL）
            available_balance: 可用余额
            signal: 交易信号
            
        Returns:
            订单信息
        """
        try:
            # 获取当前价格
            ticker = self.asterdex.get_ticker_price(symbol)
            current_price = float(ticker['price'])
            
            # 获取交易对信息
            symbol_info = self.get_symbol_info(symbol)
            if not symbol_info:
                self.logger.error(f"无法获取 {symbol} 交易对信息")
                return None
            
            # 计算仓位大小
            position_info = self.risk_manager.calculate_position_size(
                available_balance,
                current_price,
                self.leverage,
                symbol_info
            )
            
            quantity = position_info['quantity']
            
            self.logger.info(
                f"开仓信号: {symbol} {side}, "
                f"价格: {current_price:.6f}, "
                f"数量: {quantity:.6f}, "
                f"名义价值: {position_info['notional']:.2f} USDT, "
                f"保证金: {position_info['margin']:.2f} USDT"
            )
            
            # 验证订单
            is_valid, error_msg = self.risk_manager.validate_order(
                symbol,
                side,
                quantity,
                current_price,
                symbol_info
            )
            
            if not is_valid:
                self.logger.error(f"订单验证失败: {error_msg}")
                return None
            
            # 下市价单
            order = self.asterdex.place_order(
                symbol=symbol,
                side=side,
                order_type='MARKET',
                quantity=str(quantity),
                position_side='BOTH'
            )
            
            self.logger.info(f"开仓成功: {order}")
            
            # 如果启用了止损，设置止损单
            # （这里简化处理，实际应用中可以设置止损限价单）
            
            return order
        
        except Exception as e:
            self.logger.error(f"开仓失败 [{symbol}]: {e}")
            return None
    
    def _close_position(
        self,
        symbol: str,
        position: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        平仓
        
        Args:
            symbol: 交易对符号
            position: 持仓信息
            
        Returns:
            订单信息
        """
        try:
            position_amt = position['position_amt']
            
            # 确定平仓方向
            if position_amt > 0:
                # 做多持仓，平仓需要卖出
                side = 'SELL'
            else:
                # 做空持仓，平仓需要买入
                side = 'BUY'
            
            quantity = abs(position_amt)
            
            self.logger.info(
                f"平仓信号: {symbol} {side}, "
                f"数量: {quantity:.6f}, "
                f"未实现盈亏: {position['unrealized_profit']:.2f} USDT"
            )
            
            # 下市价单平仓
            order = self.asterdex.place_order(
                symbol=symbol,
                side=side,
                order_type='MARKET',
                quantity=str(quantity),
                position_side='BOTH',
                reduce_only=True
            )
            
            self.logger.info(f"平仓成功: {order}")
            
            return order
        
        except Exception as e:
            self.logger.error(f"平仓失败 [{symbol}]: {e}")
            return None
    
    def _get_ai_confirmation(
        self,
        symbol: str,
        signal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        使用 AI 进行交易信号确认（可选功能）
        
        Args:
            symbol: 交易对符号
            signal: 交易信号
            
        Returns:
            AI 分析结果
        """
        try:
            current_price = signal.get('current_price', 0)
            ma_data = signal.get('ma_data', {})
            
            # 获取市场情绪（设置超时避免阻塞）
            sentiment = self.deepseek.get_market_sentiment(symbol)
            
            # 分析交易信号
            ai_signal = self.deepseek.analyze_trading_signal(
                symbol,
                current_price,
                ma_data,
                sentiment.get('analysis', '')
            )
            
            self.logger.info(f"AI 分析结果 [{symbol}]: {ai_signal}")
            
            return ai_signal
        
        except Exception as e:
            # AI 分析失败时返回原始信号，不阻止交易
            self.logger.warning(f"AI 分析失败（降级到本地策略）: {e}")
            # 返回原始信号的动作和置信度，让本地策略决定
            return {
                'action': signal['action'], 
                'confidence': signal['confidence'], 
                'reason': f'AI不可用，使用本地策略 (错误: {str(e)[:50]})'
            }

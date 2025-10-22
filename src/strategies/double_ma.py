"""
双均线交易策略模块
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import time

from .indicators import TechnicalIndicators
from ..utils.logger import get_logger


class DoubleMaStrategy:
    """双均线交易策略"""
    
    def __init__(
        self,
        sma_periods: List[int] = [20, 60, 120],
        ema_periods: List[int] = [20, 60, 120],
        convergence_threshold: float = 2.0,
        breakout_confirmation_minutes: int = 30
    ):
        """
        初始化策略
        
        Args:
            sma_periods: SMA 周期列表
            ema_periods: EMA 周期列表
            convergence_threshold: 均线密集阈值（百分比）
            breakout_confirmation_minutes: 突破确认时间（分钟）
        """
        self.sma_periods = sma_periods
        self.ema_periods = ema_periods
        self.convergence_threshold = convergence_threshold
        self.breakout_confirmation_minutes = breakout_confirmation_minutes
        self.logger = get_logger()
        
        # 存储每个交易对的状态
        self.symbol_states = {}
    
    def analyze(
        self,
        symbol: str,
        klines: List[List],
        interval: str
    ) -> Dict[str, Any]:
        """
        分析交易信号
        
        Args:
            symbol: 交易对符号
            klines: K线数据
            interval: K线间隔
            
        Returns:
            分析结果
        """
        # 解析K线数据
        parsed_data = TechnicalIndicators.parse_klines(klines)
        
        if not parsed_data['close']:
            self.logger.warning(f"{symbol} 没有K线数据")
            return self._create_signal('HOLD', 0, "无K线数据")
        
        # 计算所有均线
        ma_data = TechnicalIndicators.calculate_all_mas(
            parsed_data['close'],
            self.sma_periods,
            self.ema_periods
        )
        
        current_price = parsed_data['close'][-1]
        
        # 获取所有均线值
        all_ma_values = [v for v in ma_data.values() if v > 0]
        
        if not all_ma_values:
            self.logger.warning(f"{symbol} 无法计算均线")
            return self._create_signal('HOLD', 0, "无法计算均线")
        
        # 检查均线是否密集
        is_convergent = TechnicalIndicators.check_ma_convergence(
            all_ma_values,
            self.convergence_threshold
        )
        
        # 计算均线平均值
        ma_avg = sum(all_ma_values) / len(all_ma_values)
        
        # 检查价格位置
        price_position = TechnicalIndicators.check_price_position(
            current_price,
            all_ma_values
        )
        
        # 获取或创建该交易对的状态
        if symbol not in self.symbol_states:
            self.symbol_states[symbol] = {
                'last_convergence_time': None,
                'breakout_direction': None,
                'breakout_time': None,
                'position': None
            }
        
        state = self.symbol_states[symbol]
        
        # 记录均线密集时间
        if is_convergent and state['last_convergence_time'] is None:
            state['last_convergence_time'] = datetime.now()
            self.logger.info(f"{symbol} 均线密集，平均值: {ma_avg:.6f}")
        
        # 如果均线不密集，重置密集时间
        if not is_convergent:
            if state['last_convergence_time']:
                self.logger.info(f"{symbol} 均线分散")
            state['last_convergence_time'] = None
        
        # 生成交易信号
        signal = self._generate_signal(
            symbol,
            current_price,
            parsed_data['close'],
            ma_avg,
            is_convergent,
            price_position,
            state,
            interval
        )
        
        # 添加额外信息
        signal['ma_data'] = ma_data
        signal['current_price'] = current_price
        signal['is_convergent'] = is_convergent
        signal['price_position'] = price_position
        
        return signal
    
    def _generate_signal(
        self,
        symbol: str,
        current_price: float,
        price_history: List[float],
        ma_avg: float,
        is_convergent: bool,
        price_position: str,
        state: Dict[str, Any],
        interval: str
    ) -> Dict[str, Any]:
        """
        生成交易信号
        
        Args:
            symbol: 交易对符号
            current_price: 当前价格
            price_history: 价格历史
            ma_avg: 均线平均值
            is_convergent: 是否密集
            price_position: 价格位置
            state: 交易对状态
            interval: K线间隔
            
        Returns:
            交易信号
        """
        now = datetime.now()
        
        # 如果有持仓，检查平仓条件
        if state['position']:
            # 平仓条件：均线再次密集
            if is_convergent:
                self.logger.info(f"{symbol} 均线再次密集，生成平仓信号")
                state['position'] = None
                state['breakout_direction'] = None
                state['breakout_time'] = None
                return self._create_signal(
                    'CLOSE',
                    80,
                    f"均线再次密集，平仓 {state['position']} 持仓"
                )
        
        # 如果没有持仓，检查开仓条件
        if not state['position']:
            # 开仓条件：
            # 1. 均线密集
            # 2. 价格突破均线
            # 3. 在确认时间内站稳
            
            if is_convergent and state['last_convergence_time']:
                # 检查向上突破
                if price_position == 'ABOVE':
                    if state['breakout_direction'] != 'UP':
                        # 检测到突破
                        has_breakout = TechnicalIndicators.check_breakout(
                            price_history,
                            ma_avg,
                            'UP'
                        )
                        
                        if has_breakout:
                            state['breakout_direction'] = 'UP'
                            state['breakout_time'] = now
                            self.logger.info(f"{symbol} 检测到向上突破，价格: {current_price:.6f}, 均线: {ma_avg:.6f}")
                    
                    # 检查是否站稳
                    if state['breakout_direction'] == 'UP' and state['breakout_time']:
                        time_since_breakout = (now - state['breakout_time']).total_seconds() / 60
                        
                        # 计算需要确认的K线数量
                        bars_needed = self._get_confirmation_bars(interval, self.breakout_confirmation_minutes)
                        
                        # 检查稳定性
                        is_stable = TechnicalIndicators.check_price_stability(
                            price_history,
                            ma_avg,
                            'ABOVE',
                            bars_needed
                        )
                        
                        if is_stable and time_since_breakout >= self.breakout_confirmation_minutes:
                            self.logger.info(f"{symbol} 向上突破确认，开多仓")
                            state['position'] = 'LONG'
                            return self._create_signal(
                                'BUY',
                                90,
                                f"价格向上突破并站稳均线 {time_since_breakout:.1f} 分钟"
                            )
                
                # 检查向下突破
                elif price_position == 'BELOW':
                    if state['breakout_direction'] != 'DOWN':
                        # 检测到突破
                        has_breakout = TechnicalIndicators.check_breakout(
                            price_history,
                            ma_avg,
                            'DOWN'
                        )
                        
                        if has_breakout:
                            state['breakout_direction'] = 'DOWN'
                            state['breakout_time'] = now
                            self.logger.info(f"{symbol} 检测到向下突破，价格: {current_price:.6f}, 均线: {ma_avg:.6f}")
                    
                    # 检查是否站稳
                    if state['breakout_direction'] == 'DOWN' and state['breakout_time']:
                        time_since_breakout = (now - state['breakout_time']).total_seconds() / 60
                        
                        # 计算需要确认的K线数量
                        bars_needed = self._get_confirmation_bars(interval, self.breakout_confirmation_minutes)
                        
                        # 检查稳定性
                        is_stable = TechnicalIndicators.check_price_stability(
                            price_history,
                            ma_avg,
                            'BELOW',
                            bars_needed
                        )
                        
                        if is_stable and time_since_breakout >= self.breakout_confirmation_minutes:
                            self.logger.info(f"{symbol} 向下突破确认，开空仓")
                            state['position'] = 'SHORT'
                            return self._create_signal(
                                'SELL',
                                90,
                                f"价格向下突破并站稳均线下方 {time_since_breakout:.1f} 分钟"
                            )
        
        # 默认持有
        return self._create_signal('HOLD', 50, "等待交易信号")
    
    def _get_confirmation_bars(self, interval: str, minutes: int) -> int:
        """
        根据K线间隔计算确认所需的K线数量
        
        Args:
            interval: K线间隔
            minutes: 确认时间（分钟）
            
        Returns:
            K线数量
        """
        interval_minutes = {
            '1m': 1, '3m': 3, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '2h': 120, '4h': 240, '6h': 360, '8h': 480,
            '12h': 720, '1d': 1440
        }
        
        interval_min = interval_minutes.get(interval, 15)
        bars = max(1, int(minutes / interval_min))
        
        return bars
    
    def _create_signal(self, action: str, confidence: int, reason: str) -> Dict[str, Any]:
        """
        创建交易信号
        
        Args:
            action: 操作（BUY/SELL/HOLD/CLOSE）
            confidence: 信心程度（0-100）
            reason: 理由
            
        Returns:
            信号字典
        """
        return {
            'action': action,
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def reset_symbol_state(self, symbol: str):
        """
        重置交易对状态
        
        Args:
            symbol: 交易对符号
        """
        if symbol in self.symbol_states:
            self.symbol_states[symbol] = {
                'last_convergence_time': None,
                'breakout_direction': None,
                'breakout_time': None,
                'position': None
            }
            self.logger.info(f"重置 {symbol} 状态")
    
    def get_symbol_state(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取交易对状态
        
        Args:
            symbol: 交易对符号
            
        Returns:
            状态字典
        """
        return self.symbol_states.get(symbol)

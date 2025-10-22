"""
技术指标计算模块
"""
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Any


class TechnicalIndicators:
    """技术指标计算类"""
    
    @staticmethod
    def sma(data: List[float], period: int) -> float:
        """
        计算简单移动平均线（SMA）
        
        Args:
            data: 价格数据
            period: 周期
            
        Returns:
            SMA 值
        """
        if len(data) < period:
            return 0.0
        
        return np.mean(data[-period:])
    
    @staticmethod
    def ema(data: List[float], period: int) -> float:
        """
        计算指数移动平均线（EMA）
        
        Args:
            data: 价格数据
            period: 周期
            
        Returns:
            EMA 值
        """
        if len(data) < period:
            return 0.0
        
        # 使用 pandas 计算 EMA
        series = pd.Series(data)
        ema_series = series.ewm(span=period, adjust=False).mean()
        return float(ema_series.iloc[-1])
    
    @staticmethod
    def calculate_all_mas(
        close_prices: List[float],
        sma_periods: List[int] = [20, 60, 120],
        ema_periods: List[int] = [20, 60, 120]
    ) -> Dict[str, float]:
        """
        计算所有移动平均线
        
        Args:
            close_prices: 收盘价列表
            sma_periods: SMA 周期列表
            ema_periods: EMA 周期列表
            
        Returns:
            包含所有均线值的字典
        """
        result = {}
        
        # 计算 SMA
        for period in sma_periods:
            result[f'sma_{period}'] = TechnicalIndicators.sma(close_prices, period)
        
        # 计算 EMA
        for period in ema_periods:
            result[f'ema_{period}'] = TechnicalIndicators.ema(close_prices, period)
        
        return result
    
    @staticmethod
    def check_ma_convergence(
        ma_values: List[float],
        threshold_percent: float = 2.0
    ) -> bool:
        """
        检查均线是否密集
        
        Args:
            ma_values: 均线值列表
            threshold_percent: 密集阈值百分比
            
        Returns:
            是否密集
        """
        if not ma_values or len(ma_values) < 2:
            return False
        
        # 过滤掉无效值
        ma_values = [v for v in ma_values if v > 0]
        if len(ma_values) < 2:
            return False
        
        # 计算均线之间的最大差异百分比
        max_value = max(ma_values)
        min_value = min(ma_values)
        
        if max_value == 0:
            return False
        
        diff_percent = ((max_value - min_value) / max_value) * 100
        
        return diff_percent <= threshold_percent
    
    @staticmethod
    def check_price_position(
        current_price: float,
        ma_values: List[float]
    ) -> str:
        """
        检查价格相对于均线的位置
        
        Args:
            current_price: 当前价格
            ma_values: 均线值列表
            
        Returns:
            位置描述（ABOVE/BELOW/CROSS）
        """
        if not ma_values:
            return 'UNKNOWN'
        
        # 过滤掉无效值
        ma_values = [v for v in ma_values if v > 0]
        if not ma_values:
            return 'UNKNOWN'
        
        # 计算均线平均值
        avg_ma = np.mean(ma_values)
        
        # 判断价格位置
        if current_price > avg_ma * 1.01:  # 高于均线 1% 以上
            return 'ABOVE'
        elif current_price < avg_ma * 0.99:  # 低于均线 1% 以上
            return 'BELOW'
        else:
            return 'CROSS'
    
    @staticmethod
    def check_breakout(
        historical_prices: List[float],
        ma_avg: float,
        direction: str = 'UP'
    ) -> bool:
        """
        检查是否发生突破
        
        Args:
            historical_prices: 历史价格列表（从旧到新）
            ma_avg: 均线平均值
            direction: 突破方向（UP/DOWN）
            
        Returns:
            是否发生突破
        """
        if len(historical_prices) < 2:
            return False
        
        previous_price = historical_prices[-2]
        current_price = historical_prices[-1]
        
        if direction == 'UP':
            # 向上突破：前一个价格在均线下方，当前价格在均线上方
            return previous_price < ma_avg and current_price > ma_avg
        else:
            # 向下突破：前一个价格在均线上方，当前价格在均线下方
            return previous_price > ma_avg and current_price < ma_avg
    
    @staticmethod
    def check_price_stability(
        recent_prices: List[float],
        ma_avg: float,
        direction: str = 'ABOVE',
        bars_count: int = 2
    ) -> bool:
        """
        检查价格是否稳定在均线某一侧
        
        Args:
            recent_prices: 最近的价格列表
            ma_avg: 均线平均值
            direction: 方向（ABOVE/BELOW）
            bars_count: 需要稳定的K线数量
            
        Returns:
            是否稳定
        """
        if len(recent_prices) < bars_count:
            return False
        
        check_prices = recent_prices[-bars_count:]
        
        if direction == 'ABOVE':
            return all(price > ma_avg for price in check_prices)
        else:
            return all(price < ma_avg for price in check_prices)
    
    @staticmethod
    def calculate_atr(
        high_prices: List[float],
        low_prices: List[float],
        close_prices: List[float],
        period: int = 14
    ) -> float:
        """
        计算平均真实波幅（ATR）
        
        Args:
            high_prices: 最高价列表
            low_prices: 最低价列表
            close_prices: 收盘价列表
            period: 周期
            
        Returns:
            ATR 值
        """
        if len(high_prices) < period + 1:
            return 0.0
        
        # 创建 DataFrame
        df = pd.DataFrame({
            'high': high_prices,
            'low': low_prices,
            'close': close_prices
        })
        
        # 计算 True Range
        df['h-l'] = df['high'] - df['low']
        df['h-pc'] = abs(df['high'] - df['close'].shift(1))
        df['l-pc'] = abs(df['low'] - df['close'].shift(1))
        
        df['tr'] = df[['h-l', 'h-pc', 'l-pc']].max(axis=1)
        
        # 计算 ATR
        atr = df['tr'].rolling(window=period).mean().iloc[-1]
        
        return float(atr) if not pd.isna(atr) else 0.0
    
    @staticmethod
    def parse_klines(klines: List[List]) -> Dict[str, List[float]]:
        """
        解析K线数据
        
        Args:
            klines: K线数据列表
            
        Returns:
            解析后的数据字典
        """
        # K线数据格式：
        # [
        #   [
        #     1499040000000,      // 开盘时间
        #     "0.01634000",       // 开盘价
        #     "0.80000000",       // 最高价
        #     "0.01575800",       // 最低价
        #     "0.01577100",       // 收盘价
        #     "148976.11427815",  // 成交量
        #     1499644799999,      // 收盘时间
        #     "2434.19055334",    // 成交额
        #     308,                // 成交笔数
        #     "1756.87402397",    // 主动买入成交量
        #     "28.46694368",      // 主动买入成交额
        #     "17928899.62484339" // 请忽略该参数
        #   ]
        # ]
        
        if not klines:
            return {
                'open_time': [],
                'open': [],
                'high': [],
                'low': [],
                'close': [],
                'volume': [],
                'close_time': []
            }
        
        return {
            'open_time': [int(k[0]) for k in klines],
            'open': [float(k[1]) for k in klines],
            'high': [float(k[2]) for k in klines],
            'low': [float(k[3]) for k in klines],
            'close': [float(k[4]) for k in klines],
            'volume': [float(k[5]) for k in klines],
            'close_time': [int(k[6]) for k in klines]
        }

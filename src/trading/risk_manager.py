"""
风险管理模块
"""
from typing import Dict, Any, Optional
from decimal import Decimal, ROUND_DOWN

from ..utils.logger import get_logger


class RiskManager:
    """风险管理器"""
    
    def __init__(
        self,
        max_leverage: int = 5,
        max_position_percent: float = 30.0,
        margin_type: str = 'ISOLATED'
    ):
        """
        初始化风险管理器
        
        Args:
            max_leverage: 最大杠杆倍数
            max_position_percent: 单币种最大保证金占用百分比
            margin_type: 保证金类型（ISOLATED/CROSSED）
        """
        self.max_leverage = max_leverage
        self.max_position_percent = max_position_percent
        self.margin_type = margin_type
        self.logger = get_logger()
    
    def calculate_position_size(
        self,
        available_balance: float,
        current_price: float,
        leverage: int,
        symbol_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        计算仓位大小
        
        Args:
            available_balance: 可用余额（USDT）
            current_price: 当前价格
            leverage: 杠杆倍数
            symbol_info: 交易对信息
            
        Returns:
            仓位信息，包含：
            - quantity: 数量
            - notional: 名义价值
            - margin: 所需保证金
        """
        # 确保杠杆不超过最大值
        leverage = min(leverage, self.max_leverage)
        
        # 计算最大可用保证金（不超过可用余额的30%）
        max_margin = available_balance * (self.max_position_percent / 100)
        
        # 计算名义价值
        notional = max_margin * leverage
        
        # 计算数量
        quantity = notional / current_price
        
        # 应用交易所的过滤器规则
        quantity = self._apply_lot_size_filter(quantity, symbol_info)
        
        # 重新计算实际值
        actual_notional = quantity * current_price
        actual_margin = actual_notional / leverage
        
        return {
            'quantity': quantity,
            'notional': actual_notional,
            'margin': actual_margin,
            'leverage': leverage
        }
    
    def _apply_lot_size_filter(
        self,
        quantity: float,
        symbol_info: Dict[str, Any]
    ) -> float:
        """
        应用交易所的LOT_SIZE过滤器
        
        Args:
            quantity: 原始数量
            symbol_info: 交易对信息
            
        Returns:
            调整后的数量
        """
        # 从 exchangeInfo 中查找 LOT_SIZE 过滤器
        filters = symbol_info.get('filters', [])
        
        for f in filters:
            if f.get('filterType') == 'LOT_SIZE':
                min_qty = float(f.get('minQty', 0))
                max_qty = float(f.get('maxQty', float('inf')))
                step_size = float(f.get('stepSize', 0.01))
                
                # 确保数量在范围内
                quantity = max(min_qty, min(quantity, max_qty))
                
                # 向下取整到 step_size
                if step_size > 0:
                    quantity = float(Decimal(str(quantity)) - Decimal(str(quantity)) % Decimal(str(step_size)))
                
                break
        
        return quantity
    
    def validate_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        symbol_info: Dict[str, Any]
    ) -> tuple[bool, str]:
        """
        验证订单是否符合交易所规则
        
        Args:
            symbol: 交易对符号
            side: 买卖方向
            quantity: 数量
            price: 价格
            symbol_info: 交易对信息
            
        Returns:
            (是否有效, 错误信息)
        """
        filters = symbol_info.get('filters', [])
        
        for f in filters:
            filter_type = f.get('filterType')
            
            # 价格过滤器
            if filter_type == 'PRICE_FILTER':
                min_price = float(f.get('minPrice', 0))
                max_price = float(f.get('maxPrice', float('inf')))
                tick_size = float(f.get('tickSize', 0.01))
                
                if price < min_price:
                    return False, f"价格 {price} 低于最小价格 {min_price}"
                if price > max_price:
                    return False, f"价格 {price} 高于最大价格 {max_price}"
                
                # 检查价格精度
                if tick_size > 0:
                    price_mod = float(Decimal(str(price)) % Decimal(str(tick_size)))
                    if price_mod != 0:
                        return False, f"价格 {price} 不符合价格步长 {tick_size}"
            
            # 数量过滤器
            elif filter_type == 'LOT_SIZE':
                min_qty = float(f.get('minQty', 0))
                max_qty = float(f.get('maxQty', float('inf')))
                step_size = float(f.get('stepSize', 0.01))
                
                if quantity < min_qty:
                    return False, f"数量 {quantity} 低于最小数量 {min_qty}"
                if quantity > max_qty:
                    return False, f"数量 {quantity} 高于最大数量 {max_qty}"
                
                # 检查数量精度
                if step_size > 0:
                    qty_mod = float(Decimal(str(quantity)) % Decimal(str(step_size)))
                    if qty_mod != 0:
                        return False, f"数量 {quantity} 不符合数量步长 {step_size}"
            
            # 名义价值过滤器
            elif filter_type == 'MIN_NOTIONAL':
                min_notional = float(f.get('notional', 0))
                notional = price * quantity
                
                if notional < min_notional:
                    return False, f"名义价值 {notional} 低于最小值 {min_notional}"
        
        return True, ""
    
    def calculate_stop_loss(
        self,
        entry_price: float,
        side: str,
        stop_loss_percent: float = 3.0
    ) -> float:
        """
        计算止损价格
        
        Args:
            entry_price: 入场价格
            side: 买卖方向（BUY/SELL）
            stop_loss_percent: 止损百分比
            
        Returns:
            止损价格
        """
        if side == 'BUY':
            # 做多：止损价格在入场价格下方
            stop_loss = entry_price * (1 - stop_loss_percent / 100)
        else:
            # 做空：止损价格在入场价格上方
            stop_loss = entry_price * (1 + stop_loss_percent / 100)
        
        return stop_loss
    
    def calculate_take_profit(
        self,
        entry_price: float,
        side: str,
        take_profit_percent: float = 10.0
    ) -> float:
        """
        计算止盈价格
        
        Args:
            entry_price: 入场价格
            side: 买卖方向（BUY/SELL）
            take_profit_percent: 止盈百分比
            
        Returns:
            止盈价格
        """
        if side == 'BUY':
            # 做多：止盈价格在入场价格上方
            take_profit = entry_price * (1 + take_profit_percent / 100)
        else:
            # 做空：止盈价格在入场价格下方
            take_profit = entry_price * (1 - take_profit_percent / 100)
        
        return take_profit
    
    def check_position_risk(
        self,
        positions: list,
        available_balance: float
    ) -> Dict[str, Any]:
        """
        检查当前持仓风险
        
        Args:
            positions: 持仓列表
            available_balance: 可用余额
            
        Returns:
            风险分析结果
        """
        total_margin = 0
        position_count = 0
        
        for pos in positions:
            position_amt = float(pos.get('positionAmt', 0))
            if position_amt != 0:
                position_count += 1
                # 计算已使用保证金
                notional = abs(float(pos.get('notional', 0)))
                leverage = float(pos.get('leverage', 1))
                margin = notional / leverage if leverage > 0 else 0
                total_margin += margin
        
        # 计算总资金
        total_balance = available_balance + total_margin
        
        # 计算保证金使用率
        margin_usage_percent = (total_margin / total_balance * 100) if total_balance > 0 else 0
        
        return {
            'position_count': position_count,
            'total_margin': total_margin,
            'available_balance': available_balance,
            'total_balance': total_balance,
            'margin_usage_percent': margin_usage_percent,
            'risk_level': self._assess_risk_level(margin_usage_percent, position_count)
        }
    
    def _assess_risk_level(self, margin_usage: float, position_count: int) -> str:
        """
        评估风险等级
        
        Args:
            margin_usage: 保证金使用率
            position_count: 持仓数量
            
        Returns:
            风险等级（LOW/MEDIUM/HIGH）
        """
        if margin_usage > 70 or position_count > 3:
            return 'HIGH'
        elif margin_usage > 50 or position_count > 2:
            return 'MEDIUM'
        else:
            return 'LOW'

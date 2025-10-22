"""
手动交易指令处理模块
支持接收手动交易指令并立即执行开仓，然后自动监控并平仓
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import os
import threading
import time

from ..utils.logger import get_logger


class OrderSide(Enum):
    """订单方向"""
    LONG = "LONG"   # 做多
    SHORT = "SHORT"  # 做空


class OrderSource(Enum):
    """订单来源"""
    API = "API"         # HTTP API
    WEBSOCKET = "WS"    # WebSocket
    FILE = "FILE"       # 文件监听
    CLI = "CLI"         # 命令行


@dataclass
class ManualOrder:
    """手动交易指令"""
    symbol: str                    # 交易对，如 BTCUSDT
    side: OrderSide                # 方向：LONG/SHORT
    quantity: Optional[float] = None    # 数量（可选，不指定则使用默认仓位大小）
    leverage: Optional[int] = None      # 杠杆（可选，不指定则使用配置的杠杆）
    stop_loss_percent: Optional[float] = None  # 止损百分比（可选）
    take_profit_percent: Optional[float] = None  # 止盈百分比（可选）
    note: Optional[str] = None          # 备注
    source: OrderSource = OrderSource.API  # 来源
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        
        # 确保 side 是 OrderSide 枚举
        if isinstance(self.side, str):
            self.side = OrderSide[self.side.upper()]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'symbol': self.symbol,
            'side': self.side.value,
            'quantity': self.quantity,
            'leverage': self.leverage,
            'stop_loss_percent': self.stop_loss_percent,
            'take_profit_percent': self.take_profit_percent,
            'note': self.note,
            'source': self.source.value,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ManualOrder':
        """从字典创建"""
        return cls(
            symbol=data['symbol'],
            side=OrderSide[data['side'].upper()],
            quantity=data.get('quantity'),
            leverage=data.get('leverage'),
            stop_loss_percent=data.get('stop_loss_percent'),
            take_profit_percent=data.get('take_profit_percent'),
            note=data.get('note'),
            source=OrderSource[data.get('source', 'API')],
            timestamp=datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else None
        )


@dataclass
class ManualPosition:
    """手动开仓的持仓记录"""
    order_id: str                  # 订单ID
    symbol: str                    # 交易对
    side: OrderSide                # 方向
    entry_price: float             # 开仓价格
    quantity: float                # 数量
    leverage: int                  # 杠杆
    stop_loss_price: Optional[float] = None   # 止损价格
    take_profit_price: Optional[float] = None  # 止盈价格
    open_time: Optional[datetime] = None
    note: Optional[str] = None
    
    def __post_init__(self):
        if self.open_time is None:
            self.open_time = datetime.now()
    
    def calculate_pnl_percent(self, current_price: float) -> float:
        """计算盈亏百分比"""
        if self.side == OrderSide.LONG:
            return ((current_price - self.entry_price) / self.entry_price) * 100
        else:  # SHORT
            return ((self.entry_price - current_price) / self.entry_price) * 100
    
    def should_close(self, current_price: float) -> bool:
        """判断是否应该平仓"""
        # 止损判断
        if self.stop_loss_price:
            if self.side == OrderSide.LONG and current_price <= self.stop_loss_price:
                return True
            if self.side == OrderSide.SHORT and current_price >= self.stop_loss_price:
                return True
        
        # 止盈判断
        if self.take_profit_price:
            if self.side == OrderSide.LONG and current_price >= self.take_profit_price:
                return True
            if self.side == OrderSide.SHORT and current_price <= self.take_profit_price:
                return True
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'side': self.side.value,
            'entry_price': self.entry_price,
            'quantity': self.quantity,
            'leverage': self.leverage,
            'stop_loss_price': self.stop_loss_price,
            'take_profit_price': self.take_profit_price,
            'open_time': self.open_time.isoformat(),
            'note': self.note
        }


class ManualOrderHandler:
    """手动交易指令处理器"""
    
    def __init__(self, trader, config: Dict[str, Any]):
        """
        初始化手动交易处理器
        
        Args:
            trader: Trader 实例
            config: 手动交易配置
        """
        self.trader = trader
        self.config = config
        self.logger = get_logger()
        
        # 手动持仓记录
        self.manual_positions: Dict[str, ManualPosition] = {}
        
        # 指令队列文件路径
        self.order_file = config.get('order_file', 'manual_orders.json')
        
        # 监控线程
        self.monitoring_thread = None
        self.file_watch_thread = None
        self.is_running = False
        
        # 默认配置
        self.default_leverage = config.get('default_leverage', 3)
        self.default_position_percent = config.get('default_position_percent', 20)
        self.check_interval = config.get('check_interval', 10)  # 检查间隔（秒）
        
        self.logger.info("✅ 手动交易处理器已初始化")
    
    def start(self):
        """启动手动交易处理器"""
        if self.is_running:
            self.logger.warning("手动交易处理器已在运行")
            return
        
        self.is_running = True
        
        # 启动持仓监控线程
        self.monitoring_thread = threading.Thread(
            target=self._monitor_positions,
            daemon=True,
            name="ManualPositionMonitor"
        )
        self.monitoring_thread.start()
        
        # 启动文件监听线程（如果启用）
        if self.config.get('enable_file_watch', True):
            self.file_watch_thread = threading.Thread(
                target=self._watch_order_file,
                daemon=True,
                name="OrderFileWatcher"
            )
            self.file_watch_thread.start()
        
        self.logger.info("🚀 手动交易处理器已启动")
        self.logger.info(f"  - 持仓监控间隔: {self.check_interval}秒")
        if self.config.get('enable_file_watch', True):
            self.logger.info(f"  - 指令文件监听: {self.order_file}")
    
    def stop(self):
        """停止手动交易处理器"""
        self.is_running = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        if self.file_watch_thread:
            self.file_watch_thread.join(timeout=5)
        
        self.logger.info("🛑 手动交易处理器已停止")
    
    def execute_manual_order(self, order: ManualOrder) -> Optional[str]:
        """
        执行手动交易指令（立即开仓）
        
        Args:
            order: 手动交易指令
            
        Returns:
            订单ID，失败返回 None
        """
        try:
            symbol = order.symbol
            side = order.side
            
            self.logger.info("=" * 60)
            self.logger.info(f"📨 收到手动交易指令")
            self.logger.info(f"  交易对: {symbol}")
            self.logger.info(f"  方向: {side.value}")
            self.logger.info(f"  来源: {order.source.value}")
            if order.note:
                self.logger.info(f"  备注: {order.note}")
            self.logger.info("=" * 60)
            
            # 获取当前价格
            ticker = self.trader.asterdex.get_ticker(symbol)
            current_price = float(ticker['lastPrice'])
            
            # 确定杠杆
            leverage = order.leverage if order.leverage else self.default_leverage
            
            # 设置杠杆
            self.trader.setup_symbol(symbol)
            if order.leverage:
                self.trader.asterdex.change_leverage(symbol, leverage)
            
            # 计算仓位大小
            if order.quantity:
                quantity = order.quantity
            else:
                # 使用默认仓位百分比计算
                account = self.trader.asterdex.get_account()
                available_balance = float(account['availableBalance'])
                position_size = available_balance * self.default_position_percent / 100
                quantity = (position_size * leverage) / current_price
            
            # 格式化数量
            symbol_info = self.trader.get_symbol_info(symbol)
            if symbol_info:
                quantity_precision = symbol_info.get('quantityPrecision', 3)
                quantity = round(quantity, quantity_precision)
            
            self.logger.info(f"📊 开仓参数:")
            self.logger.info(f"  当前价格: ${current_price:,.2f}")
            self.logger.info(f"  杠杆: {leverage}x")
            self.logger.info(f"  数量: {quantity}")
            
            # 执行开仓
            order_side_str = "BUY" if side == OrderSide.LONG else "SELL"
            
            result = self.trader.asterdex.create_order(
                symbol=symbol,
                side=order_side_str,
                order_type="MARKET",
                quantity=quantity
            )
            
            order_id = result.get('orderId')
            
            if not order_id:
                self.logger.error(f"❌ 开仓失败: 未返回订单ID")
                return None
            
            self.logger.info(f"✅ 开仓成功!")
            self.logger.info(f"  订单ID: {order_id}")
            
            # 计算止损止盈价格
            stop_loss_price = None
            take_profit_price = None
            
            if order.stop_loss_percent:
                if side == OrderSide.LONG:
                    stop_loss_price = current_price * (1 - order.stop_loss_percent / 100)
                else:
                    stop_loss_price = current_price * (1 + order.stop_loss_percent / 100)
                self.logger.info(f"  止损价格: ${stop_loss_price:,.2f} ({order.stop_loss_percent}%)")
            
            if order.take_profit_percent:
                if side == OrderSide.LONG:
                    take_profit_price = current_price * (1 + order.take_profit_percent / 100)
                else:
                    take_profit_price = current_price * (1 - order.take_profit_percent / 100)
                self.logger.info(f"  止盈价格: ${take_profit_price:,.2f} ({order.take_profit_percent}%)")
            
            # 记录持仓
            position = ManualPosition(
                order_id=order_id,
                symbol=symbol,
                side=side,
                entry_price=current_price,
                quantity=quantity,
                leverage=leverage,
                stop_loss_price=stop_loss_price,
                take_profit_price=take_profit_price,
                note=order.note
            )
            
            self.manual_positions[order_id] = position
            
            self.logger.info(f"📝 已添加到监控列表（自动监控并平仓）")
            self.logger.info("=" * 60)
            
            return order_id
            
        except Exception as e:
            self.logger.error(f"❌ 执行手动交易指令失败: {e}", exc_info=True)
            return None
    
    def _monitor_positions(self):
        """监控手动开仓的持仓（自动平仓）"""
        self.logger.info("👀 持仓监控线程已启动")
        
        while self.is_running:
            try:
                if not self.manual_positions:
                    time.sleep(self.check_interval)
                    continue
                
                # 检查每个手动持仓
                positions_to_close = []
                
                for order_id, position in self.manual_positions.items():
                    symbol = position.symbol
                    
                    # 获取当前价格
                    ticker = self.trader.asterdex.get_ticker(symbol)
                    current_price = float(ticker['lastPrice'])
                    
                    # 计算盈亏
                    pnl_percent = position.calculate_pnl_percent(current_price)
                    
                    # 判断是否应该平仓
                    should_close = position.should_close(current_price)
                    
                    if should_close:
                        self.logger.info(f"🎯 触发平仓条件:")
                        self.logger.info(f"  订单ID: {order_id}")
                        self.logger.info(f"  交易对: {symbol}")
                        self.logger.info(f"  方向: {position.side.value}")
                        self.logger.info(f"  开仓价: ${position.entry_price:,.2f}")
                        self.logger.info(f"  当前价: ${current_price:,.2f}")
                        self.logger.info(f"  盈亏: {pnl_percent:+.2f}%")
                        
                        positions_to_close.append((order_id, position, current_price))
                    else:
                        # 定期输出持仓状态
                        if int(time.time()) % 60 == 0:  # 每分钟输出一次
                            self.logger.info(f"📊 持仓状态 - {symbol}: {pnl_percent:+.2f}%")
                
                # 执行平仓
                for order_id, position, current_price in positions_to_close:
                    self._close_manual_position(order_id, position, current_price)
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"持仓监控异常: {e}", exc_info=True)
                time.sleep(self.check_interval)
    
    def _close_manual_position(self, order_id: str, position: ManualPosition, current_price: float):
        """平仓手动持仓"""
        try:
            symbol = position.symbol
            
            # 平仓方向与开仓相反
            close_side = "SELL" if position.side == OrderSide.LONG else "BUY"
            
            result = self.trader.asterdex.create_order(
                symbol=symbol,
                side=close_side,
                order_type="MARKET",
                quantity=position.quantity,
                reduce_only=True
            )
            
            close_order_id = result.get('orderId')
            
            pnl_percent = position.calculate_pnl_percent(current_price)
            
            self.logger.info("=" * 60)
            self.logger.info(f"✅ 自动平仓成功!")
            self.logger.info(f"  订单ID: {close_order_id}")
            self.logger.info(f"  交易对: {symbol}")
            self.logger.info(f"  开仓价: ${position.entry_price:,.2f}")
            self.logger.info(f"  平仓价: ${current_price:,.2f}")
            self.logger.info(f"  最终盈亏: {pnl_percent:+.2f}%")
            self.logger.info(f"  持仓时长: {datetime.now() - position.open_time}")
            self.logger.info("=" * 60)
            
            # 从监控列表移除
            del self.manual_positions[order_id]
            
        except Exception as e:
            self.logger.error(f"❌ 平仓失败: {e}", exc_info=True)
    
    def _watch_order_file(self):
        """监听指令文件"""
        self.logger.info(f"👀 开始监听指令文件: {self.order_file}")
        
        last_modified = 0
        
        while self.is_running:
            try:
                if not os.path.exists(self.order_file):
                    time.sleep(5)
                    continue
                
                current_modified = os.path.getmtime(self.order_file)
                
                if current_modified > last_modified:
                    last_modified = current_modified
                    
                    # 读取并处理指令
                    with open(self.order_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, list):
                        orders = data
                    else:
                        orders = [data]
                    
                    for order_data in orders:
                        if order_data.get('processed', False):
                            continue
                        
                        order = ManualOrder.from_dict(order_data)
                        order.source = OrderSource.FILE
                        
                        self.execute_manual_order(order)
                        
                        # 标记为已处理
                        order_data['processed'] = True
                    
                    # 写回文件
                    with open(self.order_file, 'w', encoding='utf-8') as f:
                        json.dump(orders if len(orders) > 1 else orders[0], f, indent=2)
                
                time.sleep(5)
                
            except Exception as e:
                self.logger.error(f"文件监听异常: {e}", exc_info=True)
                time.sleep(5)
    
    def get_manual_positions(self) -> List[Dict[str, Any]]:
        """获取所有手动持仓"""
        positions = []
        
        for order_id, position in self.manual_positions.items():
            try:
                ticker = self.trader.asterdex.get_ticker(position.symbol)
                current_price = float(ticker['lastPrice'])
                pnl_percent = position.calculate_pnl_percent(current_price)
                
                pos_dict = position.to_dict()
                pos_dict['current_price'] = current_price
                pos_dict['pnl_percent'] = pnl_percent
                
                positions.append(pos_dict)
            except Exception as e:
                self.logger.error(f"获取持仓信息失败: {e}")
        
        return positions
    
    def close_position_by_id(self, order_id: str) -> bool:
        """手动关闭指定持仓"""
        if order_id not in self.manual_positions:
            self.logger.warning(f"未找到订单ID: {order_id}")
            return False
        
        position = self.manual_positions[order_id]
        
        try:
            ticker = self.trader.asterdex.get_ticker(position.symbol)
            current_price = float(ticker['lastPrice'])
            
            self._close_manual_position(order_id, position, current_price)
            return True
        except Exception as e:
            self.logger.error(f"关闭持仓失败: {e}")
            return False

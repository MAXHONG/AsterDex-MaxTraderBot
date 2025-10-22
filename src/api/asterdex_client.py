"""
AsterDEX API 客户端
"""
import json
import math
import time
from typing import Dict, Any, List, Optional
import requests
from eth_abi import encode
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3

from ..utils.logger import get_logger


class AsterDexClient:
    """AsterDEX API 客户端"""
    
    def __init__(
        self,
        user: str,
        signer: str,
        private_key: str,
        api_base_url: str = 'https://fapi.asterdex.com',
        recv_window: int = 50000
    ):
        """
        初始化客户端
        
        Args:
            user: 主钱包地址
            signer: API 钱包地址
            private_key: API 钱包私钥
            api_base_url: API 基础 URL
            recv_window: 接收窗口时间（毫秒）
        """
        self.user = user
        self.signer = signer
        self.private_key = private_key
        self.api_base_url = api_base_url
        self.recv_window = recv_window
        self.logger = get_logger()
    
    def _trim_dict(self, my_dict: Dict) -> Dict:
        """
        将字典中的值转换为字符串
        
        Args:
            my_dict: 原始字典
            
        Returns:
            转换后的字典
        """
        for key in my_dict:
            value = my_dict[key]
            if isinstance(value, list):
                new_value = []
                for item in value:
                    if isinstance(item, dict):
                        new_value.append(json.dumps(self._trim_dict(item)))
                    else:
                        new_value.append(str(item))
                my_dict[key] = json.dumps(new_value)
                continue
            if isinstance(value, dict):
                my_dict[key] = json.dumps(self._trim_dict(value))
                continue
            my_dict[key] = str(value)
        return my_dict
    
    def _sign_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        对请求参数进行签名
        
        Args:
            params: 请求参数
            
        Returns:
            包含签名的参数
        """
        # 生成 nonce（微秒）
        nonce = math.trunc(time.time() * 1000000)
        
        # 过滤空值并添加必需参数
        params = {key: value for key, value in params.items() if value is not None}
        params['recvWindow'] = self.recv_window
        params['timestamp'] = int(round(time.time() * 1000))
        
        # 转换参数
        trimmed_params = self._trim_dict(params.copy())
        
        # 生成 JSON 字符串
        json_str = json.dumps(trimmed_params, sort_keys=True).replace(' ', '').replace("'", '\\"')
        
        # ABI 编码
        encoded = encode(
            ['string', 'address', 'address', 'uint256'],
            [json_str, self.user, self.signer, nonce]
        )
        
        # Keccak 哈希
        keccak_hex = Web3.keccak(encoded).hex()
        
        # 签名
        signable_msg = encode_defunct(hexstr=keccak_hex)
        signed_message = Account.sign_message(signable_message=signable_msg, private_key=self.private_key)
        
        # 添加签名参数
        params['nonce'] = nonce
        params['user'] = self.user
        params['signer'] = self.signer
        params['signature'] = '0x' + signed_message.signature.hex()
        
        return params
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求
        
        Args:
            method: HTTP 方法
            endpoint: API 端点
            params: 请求参数
            signed: 是否需要签名
            
        Returns:
            响应数据
        """
        url = self.api_base_url + endpoint
        
        if params is None:
            params = {}
        
        # 如果需要签名
        if signed:
            params = self._sign_request(params)
        
        try:
            if method == 'GET':
                response = requests.get(url, params=params, timeout=30)
            elif method == 'POST':
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'AsterDexTradingBot/1.0'
                }
                response = requests.post(url, data=params, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, data=params, timeout=30)
            else:
                raise ValueError(f"不支持的 HTTP 方法: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API 请求失败 [{method} {endpoint}]: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"响应内容: {e.response.text}")
            raise
    
    # ==================== 市场数据接口 ====================
    
    def ping(self) -> Dict[str, Any]:
        """测试连接"""
        return self._request('GET', '/fapi/v1/ping')
    
    def get_server_time(self) -> Dict[str, Any]:
        """获取服务器时间"""
        return self._request('GET', '/fapi/v1/time')
    
    def get_exchange_info(self) -> Dict[str, Any]:
        """获取交易所信息"""
        return self._request('GET', '/fapi/v1/exchangeInfo')
    
    def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 500
    ) -> List[List]:
        """
        获取K线数据
        
        Args:
            symbol: 交易对符号
            interval: K线间隔（1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M）
            start_time: 开始时间（毫秒时间戳）
            end_time: 结束时间（毫秒时间戳）
            limit: 返回数量（默认500，最大1500）
            
        Returns:
            K线数据列表
        """
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
        
        return self._request('GET', '/fapi/v1/klines', params)
    
    def get_ticker_price(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        获取最新价格
        
        Args:
            symbol: 交易对符号（可选）
            
        Returns:
            价格信息
        """
        params = {}
        if symbol:
            params['symbol'] = symbol
        
        return self._request('GET', '/fapi/v1/ticker/price', params)
    
    def get_mark_price(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        获取标记价格
        
        Args:
            symbol: 交易对符号（可选）
            
        Returns:
            标记价格信息
        """
        params = {}
        if symbol:
            params['symbol'] = symbol
        
        return self._request('GET', '/fapi/v1/premiumIndex', params)
    
    # ==================== 账户和交易接口 ====================
    
    def get_account_info(self) -> Dict[str, Any]:
        """获取账户信息"""
        return self._request('GET', '/fapi/v3/account', signed=True)
    
    def get_balance(self) -> Dict[str, Any]:
        """获取账户余额"""
        return self._request('GET', '/fapi/v3/balance', signed=True)
    
    def get_position_info(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取持仓信息
        
        Args:
            symbol: 交易对符号（可选）
            
        Returns:
            持仓信息列表
        """
        params = {}
        if symbol:
            params['symbol'] = symbol
        
        return self._request('GET', '/fapi/v3/positionRisk', params, signed=True)
    
    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: Optional[str] = None,
        position_side: str = 'BOTH',
        time_in_force: str = 'GTC',
        reduce_only: bool = False
    ) -> Dict[str, Any]:
        """
        下单
        
        Args:
            symbol: 交易对符号
            side: 买卖方向（BUY/SELL）
            order_type: 订单类型（LIMIT/MARKET/STOP/TAKE_PROFIT等）
            quantity: 数量
            price: 价格（限价单必填）
            position_side: 持仓方向（BOTH/LONG/SHORT）
            time_in_force: 有效方式（GTC/IOC/FOK）
            reduce_only: 是否只减仓
            
        Returns:
            订单信息
        """
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity,
            'positionSide': position_side,
            'reduceOnly': reduce_only
        }
        
        if price:
            params['price'] = price
        
        if order_type == 'LIMIT':
            params['timeInForce'] = time_in_force
        
        return self._request('POST', '/fapi/v3/order', params, signed=True)
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        取消订单
        
        Args:
            symbol: 交易对符号
            order_id: 订单ID
            
        Returns:
            取消结果
        """
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        
        return self._request('DELETE', '/fapi/v3/order', params, signed=True)
    
    def cancel_all_orders(self, symbol: str) -> Dict[str, Any]:
        """
        取消所有订单
        
        Args:
            symbol: 交易对符号
            
        Returns:
            取消结果
        """
        params = {'symbol': symbol}
        return self._request('DELETE', '/fapi/v3/allOpenOrders', params, signed=True)
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取未成交订单
        
        Args:
            symbol: 交易对符号（可选）
            
        Returns:
            订单列表
        """
        params = {}
        if symbol:
            params['symbol'] = symbol
        
        return self._request('GET', '/fapi/v3/openOrders', params, signed=True)
    
    def change_leverage(self, symbol: str, leverage: int) -> Dict[str, Any]:
        """
        调整杠杆倍数
        
        Args:
            symbol: 交易对符号
            leverage: 杠杆倍数
            
        Returns:
            调整结果
        """
        params = {
            'symbol': symbol,
            'leverage': leverage
        }
        
        return self._request('POST', '/fapi/v1/leverage', params, signed=True)
    
    def change_margin_type(self, symbol: str, margin_type: str) -> Dict[str, Any]:
        """
        调整保证金模式
        
        Args:
            symbol: 交易对符号
            margin_type: 保证金模式（ISOLATED/CROSSED）
            
        Returns:
            调整结果
        """
        params = {
            'symbol': symbol,
            'marginType': margin_type
        }
        
        return self._request('POST', '/fapi/v1/marginType', params, signed=True)

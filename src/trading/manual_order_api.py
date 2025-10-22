"""
手动交易 HTTP API 服务器
提供 REST API 接口接收手动交易指令
"""
from typing import Dict, Any
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

from .manual_order_handler import ManualOrderHandler, ManualOrder, OrderSource, OrderSide
from ..utils.logger import get_logger


class ManualOrderAPIHandler(BaseHTTPRequestHandler):
    """手动交易 API 请求处理器"""
    
    # 类变量，用于存储 handler 实例
    order_handler: ManualOrderHandler = None
    
    def log_message(self, format, *args):
        """重写日志方法，使用统一的日志系统"""
        logger = get_logger()
        logger.info(f"API: {format % args}")
    
    def _send_json_response(self, status_code: int, data: Dict[str, Any]):
        """发送 JSON 响应"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def _parse_request_body(self) -> Dict[str, Any]:
        """解析请求体"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        
        body = self.rfile.read(content_length)
        return json.loads(body.decode('utf-8'))
    
    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """处理 GET 请求"""
        if self.path == '/':
            # 首页 - API 文档
            self._handle_index()
        elif self.path == '/health':
            # 健康检查
            self._handle_health()
        elif self.path == '/positions':
            # 获取手动持仓列表
            self._handle_get_positions()
        else:
            self._send_json_response(404, {
                'success': False,
                'error': 'Not Found'
            })
    
    def do_POST(self):
        """处理 POST 请求"""
        if self.path == '/order':
            # 创建手动交易指令
            self._handle_create_order()
        elif self.path.startswith('/close/'):
            # 关闭持仓
            order_id = self.path.split('/')[-1]
            self._handle_close_position(order_id)
        else:
            self._send_json_response(404, {
                'success': False,
                'error': 'Not Found'
            })
    
    def _handle_index(self):
        """首页 - API 文档"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>AsterDEX Manual Trading API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                h1 { color: #333; }
                pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }
                .endpoint { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
                .method { font-weight: bold; color: #0066cc; }
            </style>
        </head>
        <body>
            <h1>🤖 AsterDEX Manual Trading API</h1>
            <p>手动交易指令 REST API 服务</p>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /health</h3>
                <p>健康检查</p>
                <pre>curl http://localhost:8080/health</pre>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /positions</h3>
                <p>获取所有手动持仓</p>
                <pre>curl http://localhost:8080/positions</pre>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">POST</span> /order</h3>
                <p>创建手动交易指令（立即开仓）</p>
                <h4>请求示例：</h4>
                <pre>
curl -X POST http://localhost:8080/order \\
  -H "Content-Type: application/json" \\
  -d '{
    "symbol": "BTCUSDT",
    "side": "LONG",
    "quantity": null,
    "leverage": 3,
    "stop_loss_percent": 2.0,
    "take_profit_percent": 5.0,
    "note": "手动开多单"
  }'
                </pre>
                <h4>参数说明：</h4>
                <ul>
                    <li><b>symbol</b>: 交易对（必填），如 BTCUSDT, ETHUSDT</li>
                    <li><b>side</b>: 方向（必填），LONG=做多, SHORT=做空</li>
                    <li><b>quantity</b>: 数量（可选），不填则使用默认仓位大小</li>
                    <li><b>leverage</b>: 杠杆（可选），不填则使用配置的杠杆</li>
                    <li><b>stop_loss_percent</b>: 止损百分比（可选），如 2.0 表示 2%</li>
                    <li><b>take_profit_percent</b>: 止盈百分比（可选），如 5.0 表示 5%</li>
                    <li><b>note</b>: 备注（可选）</li>
                </ul>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">POST</span> /close/{order_id}</h3>
                <p>手动关闭指定持仓</p>
                <pre>curl -X POST http://localhost:8080/close/123456</pre>
            </div>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def _handle_health(self):
        """健康检查"""
        self._send_json_response(200, {
            'success': True,
            'status': 'running',
            'manual_positions': len(self.order_handler.manual_positions) if self.order_handler else 0
        })
    
    def _handle_get_positions(self):
        """获取手动持仓列表"""
        try:
            if not self.order_handler:
                self._send_json_response(503, {
                    'success': False,
                    'error': 'Order handler not initialized'
                })
                return
            
            positions = self.order_handler.get_manual_positions()
            
            self._send_json_response(200, {
                'success': True,
                'positions': positions,
                'count': len(positions)
            })
        except Exception as e:
            self._send_json_response(500, {
                'success': False,
                'error': str(e)
            })
    
    def _handle_create_order(self):
        """创建手动交易指令"""
        try:
            if not self.order_handler:
                self._send_json_response(503, {
                    'success': False,
                    'error': 'Order handler not initialized'
                })
                return
            
            # 解析请求
            data = self._parse_request_body()
            
            # 验证必填字段
            if 'symbol' not in data:
                self._send_json_response(400, {
                    'success': False,
                    'error': 'Missing required field: symbol'
                })
                return
            
            if 'side' not in data:
                self._send_json_response(400, {
                    'success': False,
                    'error': 'Missing required field: side'
                })
                return
            
            # 验证方向
            if data['side'].upper() not in ['LONG', 'SHORT']:
                self._send_json_response(400, {
                    'success': False,
                    'error': 'Invalid side, must be LONG or SHORT'
                })
                return
            
            # 创建订单对象
            order = ManualOrder(
                symbol=data['symbol'],
                side=OrderSide[data['side'].upper()],
                quantity=data.get('quantity'),
                leverage=data.get('leverage'),
                stop_loss_percent=data.get('stop_loss_percent'),
                take_profit_percent=data.get('take_profit_percent'),
                note=data.get('note'),
                source=OrderSource.API
            )
            
            # 执行订单
            order_id = self.order_handler.execute_manual_order(order)
            
            if order_id:
                self._send_json_response(200, {
                    'success': True,
                    'message': 'Order created successfully',
                    'order_id': order_id,
                    'symbol': order.symbol,
                    'side': order.side.value
                })
            else:
                self._send_json_response(500, {
                    'success': False,
                    'error': 'Failed to create order'
                })
        
        except ValueError as e:
            self._send_json_response(400, {
                'success': False,
                'error': f'Invalid parameter: {str(e)}'
            })
        except Exception as e:
            self._send_json_response(500, {
                'success': False,
                'error': str(e)
            })
    
    def _handle_close_position(self, order_id: str):
        """关闭持仓"""
        try:
            if not self.order_handler:
                self._send_json_response(503, {
                    'success': False,
                    'error': 'Order handler not initialized'
                })
                return
            
            success = self.order_handler.close_position_by_id(order_id)
            
            if success:
                self._send_json_response(200, {
                    'success': True,
                    'message': f'Position {order_id} closed successfully'
                })
            else:
                self._send_json_response(404, {
                    'success': False,
                    'error': f'Position {order_id} not found'
                })
        
        except Exception as e:
            self._send_json_response(500, {
                'success': False,
                'error': str(e)
            })


class ManualOrderAPIServer:
    """手动交易 API 服务器"""
    
    def __init__(self, order_handler: ManualOrderHandler, host: str = '0.0.0.0', port: int = 8080):
        """
        初始化 API 服务器
        
        Args:
            order_handler: 手动交易处理器
            host: 监听地址
            port: 监听端口
        """
        self.order_handler = order_handler
        self.host = host
        self.port = port
        self.logger = get_logger()
        
        # 设置 handler 类变量
        ManualOrderAPIHandler.order_handler = order_handler
        
        # HTTP 服务器
        self.server = None
        self.server_thread = None
        self.is_running = False
    
    def start(self):
        """启动 API 服务器"""
        if self.is_running:
            self.logger.warning("API 服务器已在运行")
            return
        
        try:
            self.server = HTTPServer((self.host, self.port), ManualOrderAPIHandler)
            
            self.server_thread = threading.Thread(
                target=self.server.serve_forever,
                daemon=True,
                name="ManualOrderAPIServer"
            )
            self.server_thread.start()
            
            self.is_running = True
            
            self.logger.info("=" * 60)
            self.logger.info("🌐 手动交易 API 服务器已启动")
            self.logger.info(f"  地址: http://{self.host}:{self.port}")
            self.logger.info(f"  API 文档: http://localhost:{self.port}/")
            self.logger.info(f"  健康检查: http://localhost:{self.port}/health")
            self.logger.info(f"  查看持仓: http://localhost:{self.port}/positions")
            self.logger.info("=" * 60)
        
        except Exception as e:
            self.logger.error(f"启动 API 服务器失败: {e}")
            raise
    
    def stop(self):
        """停止 API 服务器"""
        if not self.is_running:
            return
        
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        
        if self.server_thread:
            self.server_thread.join(timeout=5)
        
        self.is_running = False
        self.logger.info("🛑 API 服务器已停止")

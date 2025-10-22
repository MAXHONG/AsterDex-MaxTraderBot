"""
DeepSeek API 客户端
"""
from typing import Dict, Any, List, Optional
from openai import OpenAI

from ..utils.logger import get_logger


class DeepSeekClient:
    """DeepSeek API 客户端"""
    
    def __init__(
        self,
        api_key: str,
        api_base_url: str = 'https://api.deepseek.com',
        model: str = 'deepseek-chat'
    ):
        """
        初始化客户端
        
        Args:
            api_key: API 密钥
            api_base_url: API 基础 URL
            model: 模型名称
        """
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.model = model
        self.logger = get_logger()
        
        # 初始化 OpenAI 客户端（DeepSeek 兼容 OpenAI API）
        self.client = OpenAI(
            api_key=api_key,
            base_url=api_base_url
        )
    
    def analyze_trading_signal(
        self,
        symbol: str,
        current_price: float,
        ma_data: Dict[str, float],
        market_context: str = ""
    ) -> Dict[str, Any]:
        """
        分析交易信号
        
        Args:
            symbol: 交易对符号
            current_price: 当前价格
            ma_data: 均线数据
            market_context: 市场上下文信息
            
        Returns:
            分析结果，包含：
            - action: 建议操作（BUY/SELL/HOLD）
            - confidence: 信心程度（0-100）
            - reason: 分析理由
        """
        # 构造提示词
        prompt = self._build_analysis_prompt(symbol, current_price, ma_data, market_context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "你是一个专业的加密货币交易分析师。"
                            "基于双均线交易系统和市场数据，提供专业的交易建议。"
                            "你的回答必须是 JSON 格式，包含以下字段："
                            "action（BUY/SELL/HOLD）、confidence（0-100）、reason（分析理由）"
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # 解析响应
            content = response.choices[0].message.content
            self.logger.info(f"DeepSeek 分析结果: {content}")
            
            # 尝试解析 JSON
            import json
            try:
                result = json.loads(content)
                return {
                    'action': result.get('action', 'HOLD'),
                    'confidence': result.get('confidence', 50),
                    'reason': result.get('reason', '无法获取分析理由')
                }
            except json.JSONDecodeError:
                # 如果无法解析 JSON，使用文本解析
                return self._parse_text_response(content)
        
        except Exception as e:
            self.logger.error(f"DeepSeek API 调用失败: {e}")
            return {
                'action': 'HOLD',
                'confidence': 0,
                'reason': f'API 调用失败: {str(e)}'
            }
    
    def _build_analysis_prompt(
        self,
        symbol: str,
        current_price: float,
        ma_data: Dict[str, float],
        market_context: str
    ) -> str:
        """
        构建分析提示词
        
        Args:
            symbol: 交易对符号
            current_price: 当前价格
            ma_data: 均线数据
            market_context: 市场上下文
            
        Returns:
            提示词
        """
        prompt = f"""
请分析以下加密货币交易数据，并提供交易建议：

交易对: {symbol}
当前价格: ${current_price:.6f}

均线数据:
- SMA20: ${ma_data.get('sma_20', 0):.6f}
- SMA60: ${ma_data.get('sma_60', 0):.6f}
- SMA120: ${ma_data.get('sma_120', 0):.6f}
- EMA20: ${ma_data.get('ema_20', 0):.6f}
- EMA60: ${ma_data.get('ema_60', 0):.6f}
- EMA120: ${ma_data.get('ema_120', 0):.6f}

市场上下文:
{market_context}

请基于双均线交易系统分析：
1. 当前均线是否密集（短期、中期、长期均线相互靠近）
2. 价格相对于均线的位置（突破还是跌破）
3. 趋势方向和强度

请以 JSON 格式返回你的分析结果：
{{
    "action": "BUY/SELL/HOLD",
    "confidence": 0-100的数字,
    "reason": "详细的分析理由"
}}
"""
        return prompt
    
    def _parse_text_response(self, content: str) -> Dict[str, Any]:
        """
        解析文本响应
        
        Args:
            content: 响应文本
            
        Returns:
            解析后的结果
        """
        content_lower = content.lower()
        
        # 判断操作
        action = 'HOLD'
        if 'buy' in content_lower or '买入' in content_lower or '做多' in content_lower:
            action = 'BUY'
        elif 'sell' in content_lower or '卖出' in content_lower or '做空' in content_lower:
            action = 'SELL'
        
        # 判断信心程度
        confidence = 50
        if 'strong' in content_lower or '强烈' in content_lower or '明确' in content_lower:
            confidence = 80
        elif 'weak' in content_lower or '弱' in content_lower or '谨慎' in content_lower:
            confidence = 30
        
        return {
            'action': action,
            'confidence': confidence,
            'reason': content
        }
    
    def get_market_sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        获取市场情绪分析
        
        Args:
            symbol: 交易对符号
            
        Returns:
            市场情绪分析结果
        """
        prompt = f"""
请分析 {symbol} 的当前市场情绪和趋势。
考虑以下因素：
1. 整体加密货币市场趋势
2. 该币种的历史表现
3. 可能影响价格的因素

请以简洁的方式总结市场情绪（看涨/看跌/中性）和主要原因。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的加密货币市场分析师。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            
            return {
                'sentiment': self._extract_sentiment(content),
                'analysis': content
            }
        
        except Exception as e:
            self.logger.error(f"市场情绪分析失败: {e}")
            return {
                'sentiment': 'NEUTRAL',
                'analysis': '无法获取市场情绪分析'
            }
    
    def _extract_sentiment(self, content: str) -> str:
        """
        从分析文本中提取情绪
        
        Args:
            content: 分析文本
            
        Returns:
            情绪标签（BULLISH/BEARISH/NEUTRAL）
        """
        content_lower = content.lower()
        
        bullish_keywords = ['bullish', 'positive', 'upward', '看涨', '上涨', '乐观']
        bearish_keywords = ['bearish', 'negative', 'downward', '看跌', '下跌', '悲观']
        
        bullish_count = sum(1 for keyword in bullish_keywords if keyword in content_lower)
        bearish_count = sum(1 for keyword in bearish_keywords if keyword in content_lower)
        
        if bullish_count > bearish_count:
            return 'BULLISH'
        elif bearish_count > bullish_count:
            return 'BEARISH'
        else:
            return 'NEUTRAL'

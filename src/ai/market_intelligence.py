"""
市场情报采集和分析系统

Phase 1: 让 AI 成为信息聚合器
- 采集多源市场信息
- 使用 AI 进行信息整合
- 生成结构化的市场报告
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import requests
import json

from ..api.base_ai_client import BaseAIClient
from ..utils.logger import get_logger


class MarketIntelligenceAgent:
    """
    市场情报采集和分析代理
    
    职责：
    1. 采集多源市场信息（新闻、社交媒体、链上数据）
    2. 使用 AI 进行信息整合和分析
    3. 生成结构化的市场报告
    """
    
    def __init__(self, ai_client: BaseAIClient):
        """
        初始化市场情报代理
        
        Args:
            ai_client: AI 客户端（DeepSeek 或 Grok）
        """
        self.ai = ai_client
        self.logger = get_logger()
        
        # 缓存机制（避免频繁调用外部 API）
        self.cache = {}
        self.cache_ttl = 300  # 5 分钟缓存
    
    def collect_intelligence(
        self,
        symbol: str,
        timeframe: str = "24h"
    ) -> Dict[str, Any]:
        """
        采集指定币种的市场情报
        
        Args:
            symbol: 交易对符号（如 BTCUSDT）
            timeframe: 时间范围
            
        Returns:
            {
                "news": [...],           # 新闻事件
                "sentiment": {...},      # 市场情绪
                "macro": {...},          # 宏观因素
                "timestamp": "..."       # 采集时间
            }
        """
        # 检查缓存
        cache_key = f"{symbol}_{timeframe}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if (datetime.now() - cached_time).total_seconds() < self.cache_ttl:
                self.logger.debug(f"使用缓存的市场情报: {symbol}")
                return cached_data
        
        intelligence = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "timeframe": timeframe
        }
        
        try:
            # 1. 新闻采集
            intelligence["news"] = self._collect_news(symbol, timeframe)
            
            # 2. 社交媒体情绪（模拟数据，可接入真实 API）
            intelligence["sentiment"] = self._analyze_social_sentiment(symbol)
            
            # 3. 宏观市场状态
            intelligence["macro"] = self._get_macro_context()
            
            # 缓存结果
            self.cache[cache_key] = (intelligence, datetime.now())
            
            self.logger.info(
                f"市场情报采集完成: {symbol}, "
                f"新闻 {len(intelligence['news'])} 条"
            )
            
            return intelligence
            
        except Exception as e:
            self.logger.error(f"市场情报采集失败: {e}")
            # 返回空数据
            return {
                "timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                "news": [],
                "sentiment": {},
                "macro": {},
                "error": str(e)
            }
    
    def _collect_news(self, symbol: str, timeframe: str) -> List[Dict]:
        """
        采集新闻（示例实现）
        
        注意：这里使用模拟数据
        实际部署时可接入：
        - CryptoPanic API (https://cryptopanic.com/developers/api/)
        - CoinGecko API
        - NewsAPI
        """
        news = []
        
        # 提取币种名称
        coin = symbol.replace("USDT", "").replace("BUSD", "")
        
        # 模拟新闻数据
        # 实际使用时，替换为真实 API 调用
        news.append({
            "title": f"{coin} 市场动态分析",
            "published_at": datetime.now().isoformat(),
            "source": "Crypto News",
            "sentiment": "neutral"
        })
        
        # TODO: 接入真实 API
        # try:
        #     response = requests.get(
        #         "https://cryptopanic.com/api/v1/posts/",
        #         params={
        #             "auth_token": "YOUR_TOKEN",
        #             "currencies": coin,
        #             "kind": "news"
        #         },
        #         timeout=5
        #     )
        #     if response.status_code == 200:
        #         data = response.json()
        #         for post in data.get("results", [])[:10]:
        #             news.append({
        #                 "title": post.get("title"),
        #                 "published_at": post.get("published_at"),
        #                 "source": post.get("source", {}).get("title"),
        #                 "url": post.get("url")
        #             })
        # except Exception as e:
        #     self.logger.warning(f"新闻 API 调用失败: {e}")
        
        return news
    
    def _analyze_social_sentiment(self, symbol: str) -> Dict:
        """
        分析社交媒体情绪
        
        注意：这里使用模拟数据
        实际部署时可接入：
        - LunarCrush API
        - Santiment API
        - Twitter API
        """
        sentiment = {
            "twitter_mentions": 0,
            "reddit_posts": 0,
            "overall_sentiment": "neutral",
            "trending_score": 50  # 0-100
        }
        
        # TODO: 接入真实 API
        # try:
        #     response = requests.get(
        #         "https://api.lunarcrush.com/v2",
        #         params={
        #             "data": "assets",
        #             "symbol": symbol.replace("USDT", ""),
        #             "key": "YOUR_API_KEY"
        #         },
        #         timeout=5
        #     )
        #     if response.status_code == 200:
        #         data = response.json()
        #         # 解析数据...
        # except Exception as e:
        #     self.logger.warning(f"社交情绪 API 调用失败: {e}")
        
        return sentiment
    
    def _get_macro_context(self) -> Dict:
        """
        获取宏观市场背景
        
        注意：这里使用模拟数据
        实际部署时可接入：
        - Binance API (获取市场概况)
        - Fear & Greed Index API
        - Alternative.me API
        """
        macro = {
            "btc_dominance": 50.0,  # BTC 市值占比
            "total_market_cap": 2000000000000,  # 总市值
            "fear_greed_index": 50,  # 恐惧贪婪指数 0-100
            "market_trend": "neutral"  # bullish/bearish/neutral
        }
        
        # TODO: 接入真实 API
        
        return macro
    
    def analyze_with_ai(
        self,
        symbol: str,
        intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        使用 AI 分析市场情报，生成结构化报告
        
        Args:
            symbol: 交易对符号
            intelligence: 采集的原始情报
            
        Returns:
            {
                "market_summary": "市场整体状况总结",
                "key_factors": [...],  # 关键因素
                "sentiment_score": -10 到 +10,  # 情绪评分
                "risk_level": 1-10,  # 风险等级
                "attention_points": [...],  # 注意事项
                "time_sensitivity": "low/medium/high"
            }
        """
        try:
            prompt = self._build_analysis_prompt(symbol, intelligence)
            
            # 调用 AI 分析
            analysis = self.ai.chat_completion_json(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "你是专业的加密货币市场分析师，擅长整合多源信息做出客观分析。"
                            "你的分析必须客观、数据驱动，避免过度乐观或悲观。"
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # 验证响应格式
            if "error" in analysis:
                self.logger.warning(f"AI 分析响应异常: {analysis.get('error')}")
                return self._get_default_analysis()
            
            # 确保关键字段存在
            required_fields = [
                "market_summary", "sentiment_score", "risk_level"
            ]
            for field in required_fields:
                if field not in analysis:
                    self.logger.warning(f"AI 分析缺少字段: {field}")
                    return self._get_default_analysis()
            
            self.logger.info(
                f"AI 市场分析完成: {symbol} - "
                f"情绪: {analysis.get('sentiment_score', 0)}, "
                f"风险: {analysis.get('risk_level', 5)}/10"
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"AI 分析失败: {e}")
            return self._get_default_analysis()
    
    def _build_analysis_prompt(
        self,
        symbol: str,
        intelligence: Dict[str, Any]
    ) -> str:
        """构建 AI 分析提示词"""
        
        prompt = f"""
请分析 {symbol} 的市场情报并生成报告：

采集时间: {intelligence.get('timestamp', 'N/A')}

【新闻事件】
{self._format_news(intelligence.get('news', []))}

【社交媒体情绪】
{json.dumps(intelligence.get('sentiment', {}), indent=2, ensure_ascii=False)}

【宏观市场背景】
{json.dumps(intelligence.get('macro', {}), indent=2, ensure_ascii=False)}

请以 JSON 格式输出分析结果，包括：

{{
    "market_summary": "市场整体状况的简洁总结（1-2句话）",
    "key_factors": [
        {{
            "factor": "因素名称",
            "impact": "positive/negative/neutral",
            "importance": 1-10,
            "description": "详细说明"
        }}
    ],
    "sentiment_score": -10 到 +10 的情绪评分（负数看空，正数看多，0为中性）,
    "risk_level": 1-10 的风险等级（1最低，10最高）,
    "attention_points": ["需要特别关注的点1", "需要特别关注的点2"],
    "time_sensitivity": "low/medium/high"，表示信息的时效性
}}

注意：
1. 评分必须基于数据，不要过度乐观或悲观
2. 如果信息不足，说明"信息有限，评估不确定"
3. 重点关注可能影响短期价格的因素
"""
        
        return prompt
    
    def _format_news(self, news: List[Dict]) -> str:
        """格式化新闻列表为文本"""
        if not news:
            return "无重大新闻"
        
        formatted = []
        for item in news[:5]:  # 只取前5条
            title = item.get('title', 'N/A')
            source = item.get('source', 'Unknown')
            sentiment = item.get('sentiment', 'neutral')
            formatted.append(f"- [{sentiment}] {title} (来源: {source})")
        
        return "\n".join(formatted)
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """返回默认分析结果（当 AI 分析失败时）"""
        return {
            "market_summary": "信息采集失败，使用默认分析",
            "key_factors": [],
            "sentiment_score": 0,
            "risk_level": 5,
            "attention_points": ["AI 分析不可用，建议谨慎交易"],
            "time_sensitivity": "medium"
        }

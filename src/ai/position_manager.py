"""
AI 驱动的持仓智能管理系统

Phase 3: 持续监控持仓，动态优化止损止盈
- 实时监控持仓状态
- 动态调整止损止盈
- 提供加仓/减仓建议
- 识别趋势反转信号
"""
from typing import Dict, Any, Optional, List
import json

from ..api.base_ai_client import BaseAIClient
from ..utils.logger import get_logger


class AIPositionManager:
    """
    AI 驱动的持仓管理器
    
    职责：
    1. 监控已有持仓
    2. 根据市场变化动态调整止损止盈
    3. 提供加仓/减仓建议
    4. 识别趋势反转信号
    """
    
    def __init__(self, ai_client: BaseAIClient):
        """
        初始化持仓管理器
        
        Args:
            ai_client: AI 客户端（DeepSeek 或 Grok）
        """
        self.ai = ai_client
        self.logger = get_logger()
    
    def monitor_position(
        self,
        position: Dict[str, Any],
        current_price: float,
        market_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        监控单个持仓并给出管理建议
        
        Args:
            position: 持仓信息
            current_price: 当前价格
            market_context: 市场情报（可选）
            
        Returns:
            {
                "action": "HOLD/PARTIAL_CLOSE/FULL_CLOSE/ADD",
                "percentage": 0-100,  # 如果是 PARTIAL_CLOSE/ADD
                "reason": "...",
                "stop_loss_update": {...},
                "take_profit_update": {...},
                "alerts": [...]
            }
        """
        try:
            prompt = self._build_monitoring_prompt(
                position, current_price, market_context
            )
            
            # 调用 AI 分析
            recommendation = self.ai.chat_completion_json(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "你是专业的持仓管理顾问，擅长动态优化止损止盈。"
                            "你的建议必须基于盈亏情况和市场变化，目标是保护利润、控制亏损。"
                            "优先考虑风险控制，其次才是利润最大化。"
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            # 验证响应
            if "error" in recommendation:
                self.logger.warning(f"AI 持仓建议响应异常: {recommendation.get('error')}")
                return self._get_default_recommendation()
            
            # 验证并修正建议
            recommendation = self._validate_recommendation(recommendation)
            
            symbol = position['symbol']
            action = recommendation.get('action', 'HOLD')
            
            self.logger.info(
                f"持仓管理建议: {symbol} - {action} - "
                f"{recommendation.get('reason', 'N/A')}"
            )
            
            return recommendation
            
        except Exception as e:
            self.logger.error(f"持仓监控失败: {e}")
            return self._get_default_recommendation()
    
    def _build_monitoring_prompt(
        self,
        position: Dict[str, Any],
        current_price: float,
        market_context: Optional[Dict[str, Any]]
    ) -> str:
        """构建持仓监控提示词"""
        
        symbol = position['symbol']
        entry_price = position['entry_price']
        position_amt = position['position_amt']
        pnl_pct = ((current_price - entry_price) / entry_price) * 100
        position_side = "做多" if position_amt > 0 else "做空"
        
        # 计算持仓时间（如果有）
        holding_time = position.get('holding_hours', 'N/A')
        
        prompt = f"""
你是持仓管理顾问。请分析以下持仓并给出建议：

【持仓信息】
交易对: {symbol}
持仓方向: {position_side}
入场价格: {entry_price}
当前价格: {current_price}
当前盈亏: {pnl_pct:.2f}%
持仓数量: {abs(position_amt)}
持仓时间: {holding_time} 小时（如果已知）
"""
        
        if market_context:
            prompt += f"""
【市场背景】
市场总结: {market_context.get('market_summary', 'N/A')}
情绪评分: {market_context.get('sentiment_score', 0)}/10
风险等级: {market_context.get('risk_level', 5)}/10
注意事项: {json.dumps(market_context.get('attention_points', []), ensure_ascii=False)}
"""
        else:
            prompt += "\n【市场背景】\n无市场情报\n"
        
        prompt += """
请给出持仓管理建议，以 JSON 格式输出：

{
    "action": "HOLD/PARTIAL_CLOSE/FULL_CLOSE/ADD（选择一个）",
    
    "percentage": 0-100 之间的整数（如果 action 是 PARTIAL_CLOSE 或 ADD，表示平仓或加仓的百分比）,
    
    "reason": "详细理由（为什么这样建议）",
    
    "stop_loss_update": {
        "suggested": true/false（是否建议调整止损）,
        "new_percentage": 如果建议调整，新的止损百分比（例如 -3 表示 -3%）,
        "reason": "调整理由"
    },
    
    "take_profit_update": {
        "suggested": true/false（是否建议设置分批止盈）,
        "targets": [
            {"percentage": 盈利百分比, "size": 平仓百分比, "reason": "理由"}
        ]
    },
    
    "alerts": ["预警信息1（如果有）", "预警信息2"]
}

决策原则：
1. 盈利情况：
   - 盈利 > 5%: 考虑移动止损到盈亏平衡点，或部分止盈
   - 盈利 3-5%: 考虑收紧止损保护利润
   - 盈利 < 3%: 继续持有，监控市场
   
2. 亏损情况：
   - 亏损 < -3%: 评估是否止损或等待反弹
   - 亏损 > -5%: 强烈建议止损，避免更大损失
   
3. 市场变化：
   - 如市场情绪转空/转多，需警惕趋势反转
   - 如出现重大风险事件，建议减仓或离场
   
4. 持仓时间：
   - 短期持仓（< 4小时）：等待确认
   - 中期持仓（4-24小时）：根据盈亏决定
   - 长期持仓（> 24小时）：考虑分批止盈
"""
        
        return prompt
    
    def _validate_recommendation(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """验证并修正持仓建议"""
        
        # 验证 action
        valid_actions = ["HOLD", "PARTIAL_CLOSE", "FULL_CLOSE", "ADD"]
        if "action" not in rec or rec["action"] not in valid_actions:
            rec["action"] = "HOLD"
        
        # 验证 percentage
        if rec["action"] in ["PARTIAL_CLOSE", "ADD"]:
            if "percentage" not in rec or not isinstance(rec["percentage"], (int, float)):
                rec["percentage"] = 50  # 默认 50%
            else:
                rec["percentage"] = max(10, min(100, int(rec["percentage"])))
        else:
            rec["percentage"] = 0
        
        # 确保 reason 存在
        if "reason" not in rec:
            rec["reason"] = "无具体理由"
        
        # 确保 stop_loss_update 存在
        if "stop_loss_update" not in rec:
            rec["stop_loss_update"] = {
                "suggested": False,
                "reason": "暂无调整建议"
            }
        
        # 确保 take_profit_update 存在
        if "take_profit_update" not in rec:
            rec["take_profit_update"] = {
                "suggested": False,
                "targets": []
            }
        
        # 确保 alerts 存在
        if "alerts" not in rec or not isinstance(rec["alerts"], list):
            rec["alerts"] = []
        
        return rec
    
    def _get_default_recommendation(self) -> Dict[str, Any]:
        """返回默认建议（当 AI 分析失败时）"""
        return {
            "action": "HOLD",
            "percentage": 0,
            "reason": "AI 分析失败，建议继续持有并人工监控",
            "stop_loss_update": {
                "suggested": False,
                "reason": "AI 不可用"
            },
            "take_profit_update": {
                "suggested": False,
                "targets": []
            },
            "alerts": ["⚠️ AI 持仓管理不可用，请人工监控"]
        }
    
    def batch_monitor_positions(
        self,
        positions: List[Dict[str, Any]],
        price_map: Dict[str, float],
        market_contexts: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        批量监控多个持仓
        
        Args:
            positions: 持仓列表
            price_map: 符号到当前价格的映射 {symbol: price}
            market_contexts: 符号到市场情报的映射 {symbol: context}
            
        Returns:
            符号到建议的映射 {symbol: recommendation}
        """
        recommendations = {}
        
        for position in positions:
            symbol = position['symbol']
            
            # 跳过空仓位
            if float(position.get('positionAmt', 0)) == 0:
                continue
            
            # 获取当前价格
            current_price = price_map.get(symbol)
            if not current_price:
                self.logger.warning(f"无法获取 {symbol} 当前价格，跳过监控")
                continue
            
            # 获取市场情报
            market_context = None
            if market_contexts and symbol in market_contexts:
                market_context = market_contexts[symbol]
            
            # 监控持仓
            try:
                recommendation = self.monitor_position(
                    position, current_price, market_context
                )
                recommendations[symbol] = recommendation
            except Exception as e:
                self.logger.error(f"监控 {symbol} 持仓失败: {e}")
                recommendations[symbol] = self._get_default_recommendation()
        
        return recommendations
    
    def prioritize_actions(
        self,
        recommendations: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        对持仓建议进行优先级排序
        
        Args:
            recommendations: 符号到建议的映射
            
        Returns:
            按优先级排序的建议列表
        """
        actions = []
        
        for symbol, rec in recommendations.items():
            action = rec.get('action', 'HOLD')
            
            # 设置优先级
            priority = 0
            if action == 'FULL_CLOSE':
                priority = 10  # 最高优先级
            elif action == 'PARTIAL_CLOSE':
                priority = 8
            elif action == 'ADD':
                priority = 5
            else:  # HOLD
                priority = 1
            
            # 如果有预警，提高优先级
            if rec.get('alerts'):
                priority += 2
            
            actions.append({
                'symbol': symbol,
                'action': action,
                'recommendation': rec,
                'priority': priority
            })
        
        # 按优先级排序（降序）
        actions.sort(key=lambda x: x['priority'], reverse=True)
        
        return actions

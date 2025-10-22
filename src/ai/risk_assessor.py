"""
AI 驱动的动态风险评估系统

Phase 2: 从"能不能交易"升级为"怎么交易最安全"
- 多维度风险评分
- 动态仓位调整建议
- 动态杠杆调整建议
- 止损止盈优化建议
"""
from typing import Dict, Any, Optional
import json

from ..api.base_ai_client import BaseAIClient
from ..utils.logger import get_logger


class AIRiskAssessor:
    """
    AI 驱动的动态风险评估器
    
    职责：
    1. 综合评估交易风险（市场、流动性、事件、技术）
    2. 提供动态的仓位调整建议
    3. 提供动态的杠杆调整建议
    4. 提供止损止盈优化建议
    """
    
    def __init__(self, ai_client: BaseAIClient):
        """
        初始化风险评估器
        
        Args:
            ai_client: AI 客户端（DeepSeek 或 Grok）
        """
        self.ai = ai_client
        self.logger = get_logger()
    
    def assess_trading_risk(
        self,
        symbol: str,
        signal: Dict[str, Any],
        market_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        综合评估交易风险
        
        Args:
            symbol: 交易对符号
            signal: 本地策略生成的信号
            market_context: 市场情报分析结果（可选）
            
        Returns:
            {
                "overall_risk": 1-10,  # 总体风险评分
                "risk_breakdown": {
                    "market_risk": {...},
                    "liquidity_risk": {...},
                    "event_risk": {...},
                    "technical_risk": {...}
                },
                "position_adjustment": {
                    "size_multiplier": 0.5-1.5,  # 仓位调整系数
                    "leverage_suggestion": 1-10,  # 建议杠杆
                    "stop_loss_adjustment": 0.5-2.0  # 止损调整系数
                },
                "recommendation": {
                    "action": "PROCEED/PROCEED_WITH_CAUTION/SKIP",
                    "reason": "...",
                    "conditions": [...]  # 前置条件
                }
            }
        """
        try:
            prompt = self._build_assessment_prompt(
                symbol, signal, market_context
            )
            
            # 调用 AI 进行风险评估
            assessment = self.ai.chat_completion_json(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "你是专业的风险管理专家，擅长多维度评估交易风险。"
                            "你的评估必须保守、客观，优先考虑资金安全。"
                            "风险评分要基于实际因素，不要过度乐观。"
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # 风险评估需要更保守
                max_tokens=1200
            )
            
            # 验证响应格式
            if "error" in assessment:
                self.logger.warning(f"AI 风险评估响应异常: {assessment.get('error')}")
                return self._get_conservative_assessment(signal)
            
            # 确保关键字段存在
            if "overall_risk" not in assessment:
                self.logger.warning("AI 风险评估缺少关键字段")
                return self._get_conservative_assessment(signal)
            
            # 修正不合理的值
            assessment = self._validate_assessment(assessment)
            
            self.logger.info(
                f"风险评估完成: {symbol} - "
                f"总体风险: {assessment['overall_risk']}/10, "
                f"建议: {assessment.get('recommendation', {}).get('action', 'N/A')}"
            )
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"风险评估失败: {e}")
            return self._get_conservative_assessment(signal)
    
    def _build_assessment_prompt(
        self,
        symbol: str,
        signal: Dict[str, Any],
        market_context: Optional[Dict[str, Any]]
    ) -> str:
        """构建风险评估提示词"""
        
        prompt = f"""
你是风险管理专家。请评估以下交易机会的风险：

【交易信息】
交易对: {symbol}
本地策略信号: {signal['action']} 
策略置信度: {signal.get('confidence', 0)}%
技术指标: {json.dumps(signal.get('ma_data', {}), ensure_ascii=False)}
信号理由: {signal.get('reason', 'N/A')}
"""
        
        if market_context:
            prompt += f"""
【市场情报分析】
市场总结: {market_context.get('market_summary', 'N/A')}
情绪评分: {market_context.get('sentiment_score', 0)}/10
市场风险: {market_context.get('risk_level', 5)}/10
关注点: {json.dumps(market_context.get('attention_points', []), ensure_ascii=False)}
"""
        else:
            prompt += "\n【市场情报分析】\n无额外市场情报\n"
        
        prompt += """
请进行多维度风险评估并给出建议，以 JSON 格式输出：

{
    "overall_risk": 1-10 的总体风险评分（整数，1最低10最高）,
    
    "risk_breakdown": {
        "market_risk": {
            "score": 1-10,
            "reason": "市场整体波动性、相关性风险等"
        },
        "liquidity_risk": {
            "score": 1-10,
            "reason": "交易量是否充足、滑点风险等"
        },
        "event_risk": {
            "score": 1-10,
            "reason": "近期是否有重大事件（FOMC、财报等）"
        },
        "technical_risk": {
            "score": 1-10,
            "reason": "技术指标是否可靠、是否有背离等"
        }
    },
    
    "position_adjustment": {
        "size_multiplier": 0.5-1.5 之间的数字（小数，0.5=减半，1.0=标准，1.5=增加50%）,
        "leverage_suggestion": 1-10 之间的整数,
        "stop_loss_adjustment": 0.5-2.0 之间的数字（小数，0.5=收紧50%，1.0=标准，2.0=放宽2倍）
    },
    
    "recommendation": {
        "action": "PROCEED（正常执行）或 PROCEED_WITH_CAUTION（谨慎执行）或 SKIP（跳过）",
        "reason": "建议的详细理由",
        "conditions": ["前置条件1（如果有）", "前置条件2"]
    }
}

评估原则：
1. 总体风险 = (市场风险 + 流动性风险 + 事件风险 + 技术风险) / 4
2. 风险 >= 8: 建议 SKIP
3. 风险 6-7: 建议 PROCEED_WITH_CAUTION，降低仓位和杠杆
4. 风险 <= 5: 建议 PROCEED
5. 保守为主，宁可错过机会也不冒大风险
"""
        
        return prompt
    
    def _validate_assessment(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """验证并修正评估结果"""
        
        # 确保 overall_risk 在合理范围
        if "overall_risk" in assessment:
            risk = assessment["overall_risk"]
            if not isinstance(risk, (int, float)):
                assessment["overall_risk"] = 5
            else:
                assessment["overall_risk"] = max(1, min(10, int(risk)))
        
        # 确保 position_adjustment 存在
        if "position_adjustment" not in assessment:
            assessment["position_adjustment"] = {
                "size_multiplier": 1.0,
                "leverage_suggestion": 5,
                "stop_loss_adjustment": 1.0
            }
        else:
            adj = assessment["position_adjustment"]
            # 修正 size_multiplier
            if "size_multiplier" not in adj or not isinstance(adj["size_multiplier"], (int, float)):
                adj["size_multiplier"] = 1.0
            else:
                adj["size_multiplier"] = max(0.3, min(1.5, float(adj["size_multiplier"])))
            
            # 修正 leverage_suggestion
            if "leverage_suggestion" not in adj or not isinstance(adj["leverage_suggestion"], (int, float)):
                adj["leverage_suggestion"] = 5
            else:
                adj["leverage_suggestion"] = max(1, min(10, int(adj["leverage_suggestion"])))
            
            # 修正 stop_loss_adjustment
            if "stop_loss_adjustment" not in adj or not isinstance(adj["stop_loss_adjustment"], (int, float)):
                adj["stop_loss_adjustment"] = 1.0
            else:
                adj["stop_loss_adjustment"] = max(0.5, min(2.0, float(adj["stop_loss_adjustment"])))
        
        # 确保 recommendation 存在
        if "recommendation" not in assessment:
            assessment["recommendation"] = {
                "action": "PROCEED_WITH_CAUTION",
                "reason": "评估数据不完整，建议谨慎",
                "conditions": []
            }
        else:
            rec = assessment["recommendation"]
            # 验证 action
            valid_actions = ["PROCEED", "PROCEED_WITH_CAUTION", "SKIP"]
            if "action" not in rec or rec["action"] not in valid_actions:
                rec["action"] = "PROCEED_WITH_CAUTION"
            
            # 确保 reason 存在
            if "reason" not in rec:
                rec["reason"] = "无具体理由"
            
            # 确保 conditions 存在
            if "conditions" not in rec:
                rec["conditions"] = []
        
        return assessment
    
    def _get_conservative_assessment(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        返回保守的风险评估（当 AI 评估失败时）
        
        Args:
            signal: 本地策略信号
            
        Returns:
            保守的评估结果
        """
        return {
            "overall_risk": 7,  # 偏保守
            "risk_breakdown": {
                "market_risk": {"score": 7, "reason": "AI 评估不可用，采用保守评分"},
                "liquidity_risk": {"score": 5, "reason": "未知"},
                "event_risk": {"score": 7, "reason": "未知"},
                "technical_risk": {"score": 6, "reason": "仅基于本地策略"}
            },
            "position_adjustment": {
                "size_multiplier": 0.7,  # 减少 30% 仓位
                "leverage_suggestion": 3,  # 降低杠杆
                "stop_loss_adjustment": 1.0  # 标准止损
            },
            "recommendation": {
                "action": "PROCEED_WITH_CAUTION",
                "reason": "AI 风险评估失败，采用保守策略继续",
                "conditions": ["建议密切监控持仓", "如市场快速变化应立即平仓"]
            }
        }
    
    def assess_position_risk(
        self,
        position: Dict[str, Any],
        current_price: float,
        market_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        评估现有持仓的风险
        
        Args:
            position: 持仓信息
            current_price: 当前价格
            market_context: 市场情报（可选）
            
        Returns:
            持仓风险评估结果
        """
        try:
            symbol = position['symbol']
            entry_price = position['entry_price']
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
            
            prompt = f"""
评估以下持仓的风险：

持仓信息:
- 交易对: {symbol}
- 入场价: {entry_price}
- 当前价: {current_price}
- 盈亏: {pnl_pct:.2f}%
- 持仓方向: {"做多" if position['position_amt'] > 0 else "做空"}

{f"市场背景: {json.dumps(market_context, ensure_ascii=False)}" if market_context else "无市场背景信息"}

请评估持仓风险并给出建议，JSON 格式：

{{
    "risk_level": 1-10,
    "risk_factors": ["风险因素1", "风险因素2"],
    "recommendation": "HOLD/REDUCE/CLOSE",
    "reason": "详细理由"
}}
"""
            
            assessment = self.ai.chat_completion_json(
                messages=[
                    {"role": "system", "content": "你是持仓风险管理专家"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=600
            )
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"持仓风险评估失败: {e}")
            return {
                "risk_level": 5,
                "risk_factors": ["评估失败"],
                "recommendation": "HOLD",
                "reason": "风险评估不可用，建议持有并监控"
            }

"""
策略参数自适应优化系统

Phase 4: 根据市场状态动态调整策略参数
- 优化均线周期
- 优化收敛阈值
- 优化确认时间
- 优化杠杆和仓位
"""
from typing import Dict, Any, Optional
import json

from ..api.base_ai_client import BaseAIClient
from ..utils.logger import get_logger


class StrategyParameterOptimizer:
    """
    基于市场状态的策略参数自适应优化器
    
    职责：
    1. 根据市场状态（趋势/震荡/高波动）优化参数
    2. 提供参数调整建议和理由
    3. 评估当前策略的适用性
    4. 建议策略切换时机
    """
    
    def __init__(self, ai_client: BaseAIClient):
        """
        初始化参数优化器
        
        Args:
            ai_client: AI 客户端（DeepSeek 或 Grok）
        """
        self.ai = ai_client
        self.logger = get_logger()
    
    def optimize_parameters(
        self,
        current_params: Dict[str, Any],
        market_context: Dict[str, Any],
        recent_performance: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        根据市场状态优化策略参数
        
        Args:
            current_params: 当前策略参数
            market_context: 市场情报分析
            recent_performance: 近期表现（可选）
            
        Returns:
            {
                "ma_periods": {...},           # 均线周期优化
                "convergence_threshold": {...}, # 收敛阈值优化
                "confirmation_period": {...},   # 确认时间优化
                "leverage": {...},              # 杠杆优化
                "position_size": {...},         # 仓位大小优化
                "strategy_assessment": {...}    # 策略适用性评估
            }
        """
        try:
            prompt = self._build_optimization_prompt(
                current_params, market_context, recent_performance
            )
            
            # 调用 AI 优化
            optimization = self.ai.chat_completion_json(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "你是量化策略优化专家，擅长根据市场环境动态调整参数。"
                            "你的建议必须基于市场特征，解释清楚调整理由。"
                            "参数调整要温和，避免过度优化。"
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1200
            )
            
            # 验证响应
            if "error" in optimization:
                self.logger.warning(f"AI 参数优化响应异常: {optimization.get('error')}")
                return self._get_default_optimization(current_params)
            
            # 验证优化结果
            optimization = self._validate_optimization(optimization, current_params)
            
            self.logger.info(
                f"参数优化完成 - "
                f"策略适用性: {optimization.get('strategy_assessment', {}).get('suitability', 'N/A')}"
            )
            
            return optimization
            
        except Exception as e:
            self.logger.error(f"参数优化失败: {e}")
            return self._get_default_optimization(current_params)
    
    def _build_optimization_prompt(
        self,
        current_params: Dict[str, Any],
        market_context: Dict[str, Any],
        recent_performance: Optional[Dict[str, Any]]
    ) -> str:
        """构建参数优化提示词"""
        
        prompt = f"""
你是量化策略优化专家。请根据市场状态建议策略参数调整：

【当前参数】
{json.dumps(current_params, indent=2, ensure_ascii=False)}

【市场状态】
{json.dumps(market_context, indent=2, ensure_ascii=False)}
"""
        
        if recent_performance:
            prompt += f"""
【近期表现】
{json.dumps(recent_performance, indent=2, ensure_ascii=False)}
"""
        
        prompt += """
请建议参数优化方案，以 JSON 格式输出：

{
    "ma_periods": {
        "current": [20, 60, 120],
        "suggested": [建议的周期],
        "reason": "调整理由（例如：高波动环境建议缩短周期更灵敏）"
    },
    
    "convergence_threshold": {
        "current": 2.0,
        "suggested": 建议的阈值（例如 1.5），
        "reason": "调整理由"
    },
    
    "confirmation_period": {
        "current": 1800,
        "suggested": 建议的秒数（例如 900），
        "reason": "调整理由"
    },
    
    "leverage": {
        "current": 5,
        "suggested": 建议的杠杆（1-10）,
        "reason": "调整理由"
    },
    
    "position_size_pct": {
        "current": 30,
        "suggested": 建议的百分比（10-40）,
        "reason": "调整理由"
    },
    
    "strategy_assessment": {
        "current_strategy_name": "双均线策略",
        "suitability": 0-1 之间的适用度（小数，0最不适合，1最适合）,
        "market_type": "TRENDING_UP/TRENDING_DOWN/RANGING/HIGH_VOLATILITY",
        "recommendation": "KEEP_CURRENT（保持当前）/ADJUST_PARAMS（调整参数）/CONSIDER_ALTERNATIVE（考虑其他策略）",
        "reason": "评估理由"
    },
    
    "switch_triggers": [
        "如果 BTC 突破 $50,000，建议切换到趋势跟踪模式",
        "如果波动率持续上升，建议暂停交易"
    ]
}

优化原则：
1. 均线周期：
   - 高波动/快速变化：缩短周期（例如 10, 30, 90）更灵敏
   - 低波动/稳定趋势：延长周期（例如 30, 90, 180）减少假信号
   
2. 收敛阈值：
   - 强趋势市：放宽阈值（例如 3%）增加机会
   - 震荡市：收紧阈值（例如 1%）提高质量
   
3. 确认时间：
   - 快速变化市：缩短确认（例如 15分钟）
   - 稳定市场：延长确认（例如 45分钟）
   
4. 杠杆和仓位：
   - 低风险环境：可适当提高
   - 高风险环境：必须降低
   
5. 策略适用性：
   - 趋势市：双均线策略适用度高
   - 震荡市：双均线策略容易产生假信号，适用度低
   - 高波动：所有策略都需谨慎，建议降低杠杆和仓位
"""
        
        return prompt
    
    def _validate_optimization(
        self,
        optimization: Dict[str, Any],
        current_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """验证并修正优化结果"""
        
        # 验证 ma_periods
        if "ma_periods" not in optimization:
            optimization["ma_periods"] = {
                "current": current_params.get("ma_periods", [20, 60, 120]),
                "suggested": current_params.get("ma_periods", [20, 60, 120]),
                "reason": "保持原参数"
            }
        
        # 验证 convergence_threshold
        if "convergence_threshold" not in optimization:
            optimization["convergence_threshold"] = {
                "current": current_params.get("convergence_threshold", 2.0),
                "suggested": current_params.get("convergence_threshold", 2.0),
                "reason": "保持原参数"
            }
        else:
            suggested = optimization["convergence_threshold"].get("suggested", 2.0)
            # 限制范围 0.5% - 5%
            optimization["convergence_threshold"]["suggested"] = max(0.5, min(5.0, float(suggested)))
        
        # 验证 confirmation_period
        if "confirmation_period" not in optimization:
            optimization["confirmation_period"] = {
                "current": current_params.get("confirmation_period", 1800),
                "suggested": current_params.get("confirmation_period", 1800),
                "reason": "保持原参数"
            }
        else:
            suggested = optimization["confirmation_period"].get("suggested", 1800)
            # 限制范围 300 - 3600 秒 (5分钟 - 1小时)
            optimization["confirmation_period"]["suggested"] = max(300, min(3600, int(suggested)))
        
        # 验证 leverage
        if "leverage" not in optimization:
            optimization["leverage"] = {
                "current": current_params.get("leverage", 5),
                "suggested": current_params.get("leverage", 5),
                "reason": "保持原参数"
            }
        else:
            suggested = optimization["leverage"].get("suggested", 5)
            # 限制范围 1-10
            optimization["leverage"]["suggested"] = max(1, min(10, int(suggested)))
        
        # 验证 position_size_pct
        if "position_size_pct" not in optimization:
            optimization["position_size_pct"] = {
                "current": current_params.get("position_size_pct", 30),
                "suggested": current_params.get("position_size_pct", 30),
                "reason": "保持原参数"
            }
        else:
            suggested = optimization["position_size_pct"].get("suggested", 30)
            # 限制范围 10-40%
            optimization["position_size_pct"]["suggested"] = max(10, min(40, int(suggested)))
        
        # 验证 strategy_assessment
        if "strategy_assessment" not in optimization:
            optimization["strategy_assessment"] = {
                "current_strategy_name": "双均线策略",
                "suitability": 0.7,
                "market_type": "UNKNOWN",
                "recommendation": "KEEP_CURRENT",
                "reason": "无法评估"
            }
        else:
            assessment = optimization["strategy_assessment"]
            # 验证 suitability
            if "suitability" in assessment:
                suitability = assessment["suitability"]
                if isinstance(suitability, (int, float)):
                    assessment["suitability"] = max(0, min(1, float(suitability)))
                else:
                    assessment["suitability"] = 0.7
            else:
                assessment["suitability"] = 0.7
            
            # 验证 recommendation
            valid_recommendations = ["KEEP_CURRENT", "ADJUST_PARAMS", "CONSIDER_ALTERNATIVE"]
            if "recommendation" not in assessment or assessment["recommendation"] not in valid_recommendations:
                assessment["recommendation"] = "KEEP_CURRENT"
        
        # 确保 switch_triggers 存在
        if "switch_triggers" not in optimization or not isinstance(optimization["switch_triggers"], list):
            optimization["switch_triggers"] = []
        
        return optimization
    
    def _get_default_optimization(self, current_params: Dict[str, Any]) -> Dict[str, Any]:
        """返回默认优化结果（当 AI 优化失败时）"""
        return {
            "ma_periods": {
                "current": current_params.get("ma_periods", [20, 60, 120]),
                "suggested": current_params.get("ma_periods", [20, 60, 120]),
                "reason": "AI 优化失败，保持原参数"
            },
            "convergence_threshold": {
                "current": current_params.get("convergence_threshold", 2.0),
                "suggested": current_params.get("convergence_threshold", 2.0),
                "reason": "AI 优化失败，保持原参数"
            },
            "confirmation_period": {
                "current": current_params.get("confirmation_period", 1800),
                "suggested": current_params.get("confirmation_period", 1800),
                "reason": "AI 优化失败，保持原参数"
            },
            "leverage": {
                "current": current_params.get("leverage", 5),
                "suggested": current_params.get("leverage", 5),
                "reason": "AI 优化失败，保持原参数"
            },
            "position_size_pct": {
                "current": current_params.get("position_size_pct", 30),
                "suggested": current_params.get("position_size_pct", 30),
                "reason": "AI 优化失败，保持原参数"
            },
            "strategy_assessment": {
                "current_strategy_name": "双均线策略",
                "suitability": 0.7,
                "market_type": "UNKNOWN",
                "recommendation": "KEEP_CURRENT",
                "reason": "AI 优化不可用，保持当前策略"
            },
            "switch_triggers": []
        }
    
    def should_apply_optimization(
        self,
        optimization: Dict[str, Any],
        significance_threshold: float = 0.2
    ) -> bool:
        """
        判断是否应该应用优化建议
        
        Args:
            optimization: 优化结果
            significance_threshold: 显著性阈值（参数变化比例）
            
        Returns:
            是否应该应用
        """
        # 检查策略评估建议
        assessment = optimization.get("strategy_assessment", {})
        recommendation = assessment.get("recommendation", "KEEP_CURRENT")
        
        if recommendation == "CONSIDER_ALTERNATIVE":
            self.logger.warning("AI 建议考虑其他策略，不应用参数优化")
            return False
        
        if recommendation == "KEEP_CURRENT":
            return False
        
        # 如果建议调整参数，检查变化是否显著
        # TODO: 实现变化显著性检查
        
        return True

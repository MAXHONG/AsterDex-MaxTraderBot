"""
统一的 AI 客户端基类
支持 DeepSeek 和 Grok API
"""
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from openai import OpenAI
import json

from ..utils.logger import get_logger


class BaseAIClient(ABC):
    """
    AI 客户端基类
    
    支持的模型：
    - DeepSeek (deepseek-chat)
    - Grok (grok-beta)
    """
    
    def __init__(
        self,
        api_key: str,
        api_base: str,
        model: str,
        timeout: int = 30
    ):
        """
        初始化 AI 客户端
        
        Args:
            api_key: API 密钥
            api_base: API 基础 URL
            model: 模型名称
            timeout: 超时时间（秒）
        """
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        self.timeout = timeout
        self.logger = get_logger()
        
        # 初始化 OpenAI 兼容客户端
        self.client = OpenAI(
            api_key=api_key,
            base_url=api_base,
            timeout=timeout
        )
        
        self.logger.info(f"AI 客户端初始化成功: {model} @ {api_base}")
    
    def chat_completion(
        self,
        messages: list,
        temperature: float = 0.3,
        max_tokens: int = 1000,
        response_format: Optional[Dict[str, str]] = None
    ) -> str:
        """
        通用的聊天完成方法
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            response_format: 响应格式（如 {"type": "json_object"}）
            
        Returns:
            AI 响应内容
        """
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # 只有在指定时才添加 response_format
            if response_format:
                kwargs["response_format"] = response_format
            
            response = self.client.chat.completions.create(**kwargs)
            
            content = response.choices[0].message.content
            
            return content
            
        except Exception as e:
            self.logger.error(f"AI 调用失败: {e}")
            raise
    
    def chat_completion_json(
        self,
        messages: list,
        temperature: float = 0.3,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        获取 JSON 格式的响应
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            
        Returns:
            解析后的 JSON 对象
        """
        try:
            # 尝试使用 response_format
            content = self.chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
            
            # 解析 JSON
            return json.loads(content)
            
        except Exception as e:
            self.logger.warning(f"JSON 格式响应失败，尝试普通响应: {e}")
            
            # 降级到普通响应，然后手动解析
            content = self.chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # 尝试从响应中提取 JSON
            try:
                # 查找第一个 { 和最后一个 }
                start = content.find('{')
                end = content.rfind('}')
                if start != -1 and end != -1:
                    json_str = content[start:end+1]
                    return json.loads(json_str)
                else:
                    raise ValueError("响应中未找到 JSON 对象")
            except Exception as parse_error:
                self.logger.error(f"JSON 解析失败: {parse_error}")
                # 返回一个错误对象
                return {
                    "error": "JSON 解析失败",
                    "raw_content": content[:200]  # 只返回前 200 字符
                }


class DeepSeekClient(BaseAIClient):
    """DeepSeek 客户端"""
    
    def __init__(
        self,
        api_key: str,
        api_base: str = "https://api.deepseek.com",
        model: str = "deepseek-chat",
        timeout: int = 30
    ):
        super().__init__(api_key, api_base, model, timeout)
        self.provider = "deepseek"


class GrokClient(BaseAIClient):
    """Grok 客户端"""
    
    def __init__(
        self,
        api_key: str,
        api_base: str = "https://api.x.ai/v1",
        model: str = "grok-beta",
        timeout: int = 30
    ):
        super().__init__(api_key, api_base, model, timeout)
        self.provider = "grok"


def create_ai_client(config: Dict[str, Any]) -> Optional[BaseAIClient]:
    """
    工厂方法：根据配置创建 AI 客户端
    
    Args:
        config: AI 配置字典，包含：
            - provider: "deepseek" 或 "grok"
            - api_key: API 密钥
            - api_base: API 基础 URL（可选）
            - model: 模型名称（可选）
            - timeout: 超时时间（可选）
    
    Returns:
        AI 客户端实例，如果配置无效则返回 None
    """
    logger = get_logger()
    
    if not config or not config.get('api_key'):
        logger.warning("未配置 AI API 密钥")
        return None
    
    provider = config.get('provider', 'deepseek').lower()
    api_key = config['api_key']
    api_base = config.get('api_base', '')
    model = config.get('model', '')
    timeout = config.get('timeout', 30)
    
    try:
        if provider == 'deepseek':
            client = DeepSeekClient(
                api_key=api_key,
                api_base=api_base or "https://api.deepseek.com",
                model=model or "deepseek-chat",
                timeout=timeout
            )
        elif provider == 'grok':
            client = GrokClient(
                api_key=api_key,
                api_base=api_base or "https://api.x.ai/v1",
                model=model or "grok-beta",
                timeout=timeout
            )
        else:
            logger.error(f"不支持的 AI 提供商: {provider}")
            return None
        
        logger.info(f"✅ {provider.upper()} 客户端创建成功")
        return client
        
    except Exception as e:
        logger.error(f"创建 AI 客户端失败: {e}")
        return None

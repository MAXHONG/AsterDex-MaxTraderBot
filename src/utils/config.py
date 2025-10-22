"""
配置加载模块
"""
import json
import os
from typing import Dict, Any


class Config:
    """配置管理类"""
    
    def __init__(self, config_path: str = None):
        """
        初始化配置
        
        Args:
            config_path: 配置文件路径
        """
        if config_path is None:
            # 默认配置路径
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(base_dir, 'config', 'config.json')
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get(self, key: str, default=None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键，支持点号分隔的嵌套键，如 'asterdex.user'
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    @property
    def asterdex(self) -> Dict[str, Any]:
        """获取 AsterDEX 配置"""
        return self.config.get('asterdex', {})
    
    @property
    def deepseek(self) -> Dict[str, Any]:
        """获取 DeepSeek 配置"""
        return self.config.get('deepseek', {})
    
    @property
    def trading(self) -> Dict[str, Any]:
        """获取交易配置"""
        return self.config.get('trading', {})
    
    @property
    def strategies(self) -> Dict[str, Any]:
        """获取策略配置"""
        return self.config.get('strategies', {})
    
    @property
    def risk_management(self) -> Dict[str, Any]:
        """获取风险管理配置"""
        return self.config.get('risk_management', {})
    
    @property
    def logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.config.get('logging', {})


# 全局配置实例
_config_instance = None


def get_config(config_path: str = None) -> Config:
    """
    获取配置实例（单例模式）
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        Config 实例
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = Config(config_path)
    
    return _config_instance

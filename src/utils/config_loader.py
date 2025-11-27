"""
配置加载器模块
负责加载配置文件和环境变量
"""
import os
import yaml
from dotenv import load_dotenv
from typing import Dict, Any


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.env_vars: Dict[str, str] = {}
        
    def load(self) -> Dict[str, Any]:
        """
        加载配置
        
        Returns:
            配置字典
        """
        # 加载环境变量
        load_dotenv()
        
        # 加载YAML配置
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 加载环境变量中的API密钥
        self._load_env_vars()
        
        return self.config
    
    def _load_env_vars(self):
        """加载环境变量"""
        # Binance
        self.env_vars['binance_api_key'] = os.getenv('BINANCE_API_KEY', '')
        self.env_vars['binance_api_secret'] = os.getenv('BINANCE_API_SECRET', '')
        
        # OKX
        self.env_vars['okx_api_key'] = os.getenv('OKX_API_KEY', '')
        self.env_vars['okx_api_secret'] = os.getenv('OKX_API_SECRET', '')
        self.env_vars['okx_passphrase'] = os.getenv('OKX_PASSPHRASE', '')
        
        # Bitget
        self.env_vars['bitget_api_key'] = os.getenv('BITGET_API_KEY', '')
        self.env_vars['bitget_api_secret'] = os.getenv('BITGET_API_SECRET', '')
        self.env_vars['bitget_passphrase'] = os.getenv('BITGET_PASSPHRASE', '')
    
    def get_exchange_config(self, exchange_name: str) -> Dict[str, str]:
        """
        获取交易所配置
        
        Args:
            exchange_name: 交易所名称
            
        Returns:
            交易所配置字典
        """
        exchange_name = exchange_name.lower()
        
        if exchange_name == 'binance':
            return {
                'api_key': self.env_vars['binance_api_key'],
                'api_secret': self.env_vars['binance_api_secret']
            }
        elif exchange_name == 'okx':
            return {
                'api_key': self.env_vars['okx_api_key'],
                'api_secret': self.env_vars['okx_api_secret'],
                'passphrase': self.env_vars['okx_passphrase']
            }
        elif exchange_name == 'bitget':
            return {
                'api_key': self.env_vars['bitget_api_key'],
                'api_secret': self.env_vars['bitget_api_secret'],
                'passphrase': self.env_vars['bitget_passphrase']
            }
        else:
            raise ValueError(f"Unsupported exchange: {exchange_name}")
    
    def validate(self) -> bool:
        """
        验证配置
        
        Returns:
            配置是否有效
        """
        # 检查必需的配置项
        required_keys = ['strategy', 'exchange', 'scheduler', 'ahr999', 'logging']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")
        
        # 检查交易所API密钥
        exchange_name = self.config['exchange']['name']
        exchange_config = self.get_exchange_config(exchange_name)
        
        if not exchange_config['api_key'] or not exchange_config['api_secret']:
            raise ValueError(f"Missing API credentials for {exchange_name}")
        
        return True
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置项（支持点号路径）
        
        Args:
            key_path: 配置键路径，如 "strategy.dca_threshold"
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value

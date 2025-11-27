"""
交易所工厂类
根据配置创建对应的交易所实例
"""
from typing import Dict
from src.exchanges.base_exchange import BaseExchange
from src.exchanges.binance_exchange import BinanceExchange
from src.exchanges.okx_exchange import OKXExchange
from src.exchanges.bitget_exchange import BitgetExchange


class ExchangeFactory:
    """交易所工厂"""
    
    @staticmethod
    def create_exchange(exchange_name: str, credentials: Dict[str, str]) -> BaseExchange:
        """
        创建交易所实例
        
        Args:
            exchange_name: 交易所名称 (binance/okx/bitget)
            credentials: API凭证字典
            
        Returns:
            交易所实例
        """
        exchange_name = exchange_name.lower()
        
        if exchange_name == 'binance':
            return BinanceExchange(
                api_key=credentials['api_key'],
                api_secret=credentials['api_secret']
            )
        elif exchange_name == 'okx':
            return OKXExchange(
                api_key=credentials['api_key'],
                api_secret=credentials['api_secret'],
                passphrase=credentials.get('passphrase', '')
            )
        elif exchange_name == 'bitget':
            return BitgetExchange(
                api_key=credentials['api_key'],
                api_secret=credentials['api_secret'],
                passphrase=credentials.get('passphrase', '')
            )
        else:
            raise ValueError(f"Unsupported exchange: {exchange_name}")

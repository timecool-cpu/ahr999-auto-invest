"""
交易所基类
定义统一的交易所接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional
from src.utils.logger import get_logger


class BaseExchange(ABC):
    """交易所基类"""
    
    def __init__(self, api_key: str, api_secret: str, passphrase: Optional[str] = None):
        """
        初始化交易所
        
        Args:
            api_key: API密钥
            api_secret: API密钥secret
            passphrase: API密码（部分交易所需要）
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.logger = get_logger()
        self.exchange = None
    
    @abstractmethod
    def connect(self) -> bool:
        """
        连接到交易所
        
        Returns:
            是否连接成功
        """
        pass
    
    @abstractmethod
    def get_balance(self, currency: str = "USDT") -> float:
        """
        获取账户余额
        
        Args:
            currency: 币种
            
        Returns:
            余额
        """
        pass
    
    @abstractmethod
    def market_buy(self, symbol: str, amount_usdt: float) -> Dict:
        """
        市价买入
        
        Args:
            symbol: 交易对，如 "BTC/USDT"
            amount_usdt: 买入金额（USDT）
            
        Returns:
            订单信息
        """
        pass
    
    @abstractmethod
    def get_ticker(self, symbol: str) -> Dict:
        """
        获取行情信息
        
        Args:
            symbol: 交易对
            
        Returns:
            行情信息
        """
        pass
    
    def test_connection(self) -> bool:
        """
        测试连接
        
        Returns:
            是否连接成功
        """
        try:
            self.connect()
            balance = self.get_balance("USDT")
            self.logger.info(f"Connection test successful. USDT balance: {balance}")
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False

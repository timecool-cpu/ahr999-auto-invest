"""
Bitget交易所实现
"""
from typing import Dict
import ccxt
from src.exchanges.base_exchange import BaseExchange


class BitgetExchange(BaseExchange):
    """Bitget交易所"""
    
    def connect(self) -> bool:
        """连接到Bitget"""
        try:
            self.exchange = ccxt.bitget({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'password': self.passphrase,  # Bitget需要passphrase
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',  # 现货交易
                }
            })
            
            # 测试连接
            self.exchange.load_markets()
            self.logger.info("Connected to Bitget")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Bitget: {str(e)}")
            raise
    
    def get_balance(self, currency: str = "USDT") -> float:
        """获取账户余额"""
        try:
            if not self.exchange:
                self.connect()
            
            balance = self.exchange.fetch_balance()
            free_balance = balance['free'].get(currency, 0)
            
            self.logger.debug(f"Bitget {currency} balance: {free_balance}")
            return free_balance
            
        except Exception as e:
            self.logger.error(f"Failed to get balance from Bitget: {str(e)}")
            raise
    
    def market_buy(self, symbol: str, amount_usdt: float) -> Dict:
        """
        市价买入
        
        Args:
            symbol: 交易对，如 "BTC/USDT"
            amount_usdt: 买入金额（USDT）
            
        Returns:
            订单信息
        """
        try:
            if not self.exchange:
                self.connect()
            
            # 获取当前价格以计算数量
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            # 计算购买数量
            amount = amount_usdt / current_price
            
            # 创建市价买单
            order = self.exchange.create_market_buy_order(symbol, amount)
            
            self.logger.info(
                f"Bitget market buy order created: {symbol}, "
                f"amount: {amount_usdt} USDT (~{amount} BTC), order_id: {order['id']}"
            )
            
            return order
            
        except Exception as e:
            self.logger.error(f"Failed to create market buy order on Bitget: {str(e)}")
            raise
    
    def get_ticker(self, symbol: str) -> Dict:
        """获取行情信息"""
        try:
            if not self.exchange:
                self.connect()
            
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker
            
        except Exception as e:
            self.logger.error(f"Failed to get ticker from Bitget: {str(e)}")
            raise

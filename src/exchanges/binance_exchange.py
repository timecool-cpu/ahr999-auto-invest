"""
Binance交易所实现
"""
from typing import Dict
import ccxt
from src.exchanges.base_exchange import BaseExchange


class BinanceExchange(BaseExchange):
    """Binance交易所"""
    
    def connect(self) -> bool:
        """连接到Binance"""
        try:
            self.exchange = ccxt.binance({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',  # 现货交易
                }
            })
            
            # 测试连接
            self.exchange.load_markets()
            self.logger.info("Connected to Binance")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Binance: {str(e)}")
            raise
    
    def get_balance(self, currency: str = "USDT") -> float:
        """获取账户余额"""
        try:
            if not self.exchange:
                self.connect()
            
            balance = self.exchange.fetch_balance()
            free_balance = balance['free'].get(currency, 0)
            
            self.logger.debug(f"Binance {currency} balance: {free_balance}")
            return free_balance
            
        except Exception as e:
            self.logger.error(f"Failed to get balance from Binance: {str(e)}")
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
            
            # 使用市价买单（按金额买入）
            order = self.exchange.create_market_buy_order(
                symbol,
                None,  # amount参数设为None
                {
                    'quoteOrderQty': amount_usdt  # 指定USDT金额
                }
            )
            
            self.logger.info(
                f"Binance market buy order created: {symbol}, "
                f"amount: {amount_usdt} USDT, order_id: {order['id']}"
            )
            
            return order
            
        except Exception as e:
            self.logger.error(f"Failed to create market buy order on Binance: {str(e)}")
            raise
    
    def get_ticker(self, symbol: str) -> Dict:
        """获取行情信息"""
        try:
            if not self.exchange:
                self.connect()
            
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker
            
        except Exception as e:
            self.logger.error(f"Failed to get ticker from Binance: {str(e)}")
            raise

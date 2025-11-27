"""
价格数据获取模块
从交易所获取BTC的实时价格和历史价格数据
"""
from typing import List, Tuple
import ccxt
from datetime import datetime, timedelta
import time
from src.utils.logger import get_logger


class PriceFetcher:
    """价格数据获取器"""
    
    def __init__(self, exchange_name: str = "binance"):
        """
        初始化价格获取器
        
        Args:
            exchange_name: 交易所名称
        """
        self.logger = get_logger()
        self.exchange_name = exchange_name.lower()
        
        # 使用CCXT创建交易所实例（公开API，无需密钥）
        exchange_class = getattr(ccxt, self.exchange_name)
        self.exchange = exchange_class({
            'enableRateLimit': True,
        })
        
        self.logger.info(f"Price fetcher initialized for {self.exchange_name}")
    
    def get_current_price(self, symbol: str = "BTC/USDT") -> float:
        """
        获取当前价格
        
        Args:
            symbol: 交易对
            
        Returns:
            当前价格
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['last']
            self.logger.debug(f"Current {symbol} price: {price}")
            return price
        except Exception as e:
            self.logger.error(f"Error fetching current price: {str(e)}")
            raise
    
    def get_historical_prices(self, symbol: str = "BTC/USDT", 
                            days: int = 400) -> List[Tuple[datetime, float]]:
        """
        获取历史价格数据
        
        Args:
            symbol: 交易对
            days: 获取天数
            
        Returns:
            历史价格列表 [(日期, 价格), ...]
        """
        try:
            self.logger.info(f"Fetching {days} days of historical data for {symbol}")
            
            # 计算开始时间（毫秒时间戳）
            since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            
            # 获取日K线数据
            ohlcv = []
            limit = 1000  # 每次请求的最大数量
            
            while True:
                batch = self.exchange.fetch_ohlcv(
                    symbol, 
                    timeframe='1d',
                    since=since,
                    limit=limit
                )
                
                if not batch:
                    break
                
                ohlcv.extend(batch)
                
                # 如果返回数据少于limit，说明已经获取完毕
                if len(batch) < limit:
                    break
                
                # 更新since为最后一条数据的时间戳
                since = batch[-1][0] + 1
                
                # 避免请求过快
                time.sleep(self.exchange.rateLimit / 1000)
            
            # 转换为 (日期, 收盘价) 格式
            prices = []
            for candle in ohlcv:
                timestamp = candle[0]
                close_price = candle[4]  # OHLCV中第5个是收盘价
                date = datetime.fromtimestamp(timestamp / 1000)
                prices.append((date, close_price))
            
            self.logger.info(f"Fetched {len(prices)} days of historical data")
            return prices
            
        except Exception as e:
            self.logger.error(f"Error fetching historical prices: {str(e)}")
            raise
    
    def get_ohlcv(self, symbol: str = "BTC/USDT", 
                  timeframe: str = "1d", 
                  limit: int = 400) -> List[List]:
        """
        获取OHLCV数据
        
        Args:
            symbol: 交易对
            timeframe: 时间周期
            limit: 数据条数
            
        Returns:
            OHLCV数据列表
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            self.logger.debug(f"Fetched {len(ohlcv)} OHLCV candles")
            return ohlcv
        except Exception as e:
            self.logger.error(f"Error fetching OHLCV data: {str(e)}")
            raise

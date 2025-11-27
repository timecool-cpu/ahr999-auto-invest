"""
AHR999指标计算模块
计算AHR999指数：(当前价格/200日定投成本) * (当前价格/拟合价格)
"""
from typing import List, Tuple
from datetime import datetime, timedelta
import numpy as np
from src.data.price_fetcher import PriceFetcher
from src.utils.logger import get_logger


class AHR999Calculator:
    """AHR999指标计算器"""
    
    # Bitcoin创世区块日期
    GENESIS_DATE = datetime(2009, 1, 3)
    
    def __init__(self, price_fetcher: PriceFetcher, ma_days: int = 200):
        """
        初始化AHR999计算器
        
        Args:
            price_fetcher: 价格获取器
            ma_days: 移动平均天数
        """
        self.price_fetcher = price_fetcher
        self.ma_days = ma_days
        self.logger = get_logger()
    
    def calculate(self, symbol: str = "BTC/USDT") -> Tuple[float, dict]:
        """
        计算AHR999指标
        
        Args:
            symbol: 交易对
            
        Returns:
            (AHR999值, 详细信息字典)
        """
        try:
            # 获取当前价格
            current_price = self.price_fetcher.get_current_price(symbol)
            
            # 获取历史价格数据
            history_days = self.ma_days + 50  # 多获取一些数据以确保足够
            historical_prices = self.price_fetcher.get_historical_prices(
                symbol, 
                days=history_days
            )
            
            # 确保有足够的历史数据
            if len(historical_prices) < self.ma_days:
                raise ValueError(
                    f"Insufficient historical data: {len(historical_prices)} days, "
                    f"required: {self.ma_days} days"
                )
            
            # 计算200日移动平均价格（定投成本）
            recent_prices = [price for _, price in historical_prices[-self.ma_days:]]
            ma_price = np.mean(recent_prices)
            
            # 计算拟合价格
            fitted_price = self._calculate_fitted_price(historical_prices)
            
            # 计算AHR999
            ahr999 = (current_price / ma_price) * (current_price / fitted_price)
            
            # 详细信息
            details = {
                'current_price': current_price,
                'ma_price': ma_price,
                'fitted_price': fitted_price,
                'ahr999': ahr999,
                'timestamp': datetime.now(),
                'data_points': len(historical_prices)
            }
            
            self.logger.info(
                f"AHR999 calculated: {ahr999:.4f} | "
                f"Current: ${current_price:.2f} | "
                f"MA{self.ma_days}: ${ma_price:.2f} | "
                f"Fitted: ${fitted_price:.2f}"
            )
            
            return ahr999, details
            
        except Exception as e:
            self.logger.error(f"Error calculating AHR999: {str(e)}")
            raise
    
    def _calculate_fitted_price(self, historical_prices: List[Tuple[datetime, float]]) -> float:
        """
        计算BTC拟合价格（使用AHR999标准公式）
        
        标准拟合价格公式：Price = 10^(5.84 * log10(coin_age_days) - 17.01)
        其中coin_age_days是从比特币创世区块（2009-01-03）到现在的天数
        
        Args:
            historical_prices: 历史价格数据（用于向后兼容，实际不使用）
            
        Returns:
            拟合价格
        """
        # 计算当前距离创世区块的天数
        days_since_genesis = (datetime.now() - self.GENESIS_DATE).days
        
        # 使用AHR999标准公式: Price = 10^(5.84 * log10(days) - 17.01)
        if days_since_genesis > 0:
            fitted_price = 10 ** (5.84 * np.log10(days_since_genesis) - 17.01)
        else:
            fitted_price = 1  # fallback
        
        self.logger.debug(
            f"Fitted price calculation: days_since_genesis={days_since_genesis}, "
            f"fitted_price=${fitted_price:.2f}"
        )
        
        return fitted_price
    
    def get_investment_suggestion(self, ahr999: float, 
                                 dca_threshold: float = 1.0,
                                 bottom_threshold: float = 0.45) -> Tuple[str, float]:
        """
        根据AHR999值获取投资建议
        
        Args:
            ahr999: AHR999指标值
            dca_threshold: 定投线阈值
            bottom_threshold: 抄底线阈值
            
        Returns:
            (建议类型, 建议金额)
            建议类型: 'BOTTOM' (抄底), 'DCA' (定投), 'HOLD' (观望)
        """
        if ahr999 < bottom_threshold:
            return 'BOTTOM', 200.0
        elif ahr999 < dca_threshold:
            return 'DCA', 100.0
        else:
            return 'HOLD', 0.0

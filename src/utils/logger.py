"""
日志记录器模块
提供统一的日志记录功能
"""
import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
import colorlog


class Logger:
    """日志记录器"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, log_dir: str = "logs", log_level: str = "INFO"):
        """
        初始化日志记录器
        
        Args:
            log_dir: 日志目录
            log_level: 日志级别
        """
        if hasattr(self, '_initialized'):
            return
            
        self.log_dir = log_dir
        self.log_level = getattr(logging, log_level.upper())
        self.logger = logging.getLogger("AHR999AutoInvest")
        self.logger.setLevel(self.log_level)
        self.logger.handlers = []  # 清除已有的handlers
        
        # 创建日志目录
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 设置日志格式
        self._setup_handlers()
        
        self._initialized = True
    
    def _setup_handlers(self):
        """设置日志处理器"""
        # 文件处理器
        log_file = os.path.join(
            self.log_dir,
            f"investment_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(file_formatter)
        
        # 控制台处理器（带颜色）
        console_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(console_formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        """调试日志"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """信息日志"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """警告日志"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """错误日志"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """严重错误日志"""
        self.logger.critical(message)
    
    def log_trade(self, exchange: str, symbol: str, amount: float, 
                  price: float, total: float, ahr999: float):
        """
        记录交易日志
        
        Args:
            exchange: 交易所
            symbol: 交易对
            amount: 买入数量
            price: 买入价格
            total: 总支出
            ahr999: AHR999指标值
        """
        message = (
            f"TRADE EXECUTED | Exchange: {exchange} | Symbol: {symbol} | "
            f"Amount: {amount:.8f} | Price: {price:.2f} | "
            f"Total: {total:.2f} USDT | AHR999: {ahr999:.4f}"
        )
        self.info(message)
    
    def log_decision(self, ahr999: float, decision: str, reason: str):
        """
        记录决策日志
        
        Args:
            ahr999: AHR999指标值
            decision: 决策（BUY_100/BUY_200/HOLD）
            reason: 原因
        """
        message = f"DECISION | AHR999: {ahr999:.4f} | Decision: {decision} | Reason: {reason}"
        self.info(message)


# 全局日志实例
_global_logger = None


def get_logger(log_dir: str = "logs", log_level: str = "INFO") -> Logger:
    """
    获取全局日志实例
    
    Args:
        log_dir: 日志目录
        log_level: 日志级别
        
    Returns:
        Logger实例
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = Logger(log_dir, log_level)
    return _global_logger

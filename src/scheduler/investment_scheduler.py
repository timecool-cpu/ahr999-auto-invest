"""
定时调度器模块
负责定时执行定投策略
"""
import schedule
import time
from datetime import datetime
import pytz
from typing import Callable
from src.utils.logger import get_logger


class InvestmentScheduler:
    """定时调度器"""
    
    def __init__(self, 
                 execute_func: Callable,
                 hour: int = 0,
                 minute: int = 0,
                 timezone: str = "Asia/Shanghai"):
        """
        初始化调度器
        
        Args:
            execute_func: 执行函数
            hour: 执行小时（24小时制）
            minute: 执行分钟
            timezone: 时区
        """
        self.execute_func = execute_func
        self.hour = hour
        self.minute = minute
        self.timezone = pytz.timezone(timezone)
        self.logger = get_logger()
        
        self.logger.info(
            f"Scheduler initialized: {hour:02d}:{minute:02d} {timezone}"
        )
    
    def schedule_daily(self):
        """设置每日定时任务"""
        time_str = f"{self.hour:02d}:{self.minute:02d}"
        schedule.every().day.at(time_str).do(self._run_with_error_handling)
        
        self.logger.info(f"Daily task scheduled at {time_str}")
    
    def _run_with_error_handling(self):
        """带错误处理的执行函数"""
        try:
            self.logger.info(f"Scheduled task started at {datetime.now()}")
            self.execute_func()
            self.logger.info("Scheduled task completed successfully")
        except Exception as e:
            self.logger.error(f"Error in scheduled task: {str(e)}")
    
    def run_forever(self):
        """
        永久运行调度器
        """
        self.logger.info("Scheduler started, waiting for scheduled time...")
        self.logger.info("Press Ctrl+C to stop")
        
        # 显示下次执行时间
        next_run = schedule.next_run()
        if next_run:
            self.logger.info(f"Next run scheduled at: {next_run}")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            self.logger.info("Scheduler stopped by user")
    
    def run_once(self):
        """立即执行一次"""
        self.logger.info("Running task immediately...")
        self._run_with_error_handling()

"""
定投策略模块
根据AHR999指标执行定投策略
"""
from typing import Dict, Optional
from src.data.ahr999_calculator import AHR999Calculator
from src.exchanges.base_exchange import BaseExchange
from src.utils.logger import get_logger
from datetime import datetime
import json
import os


class InvestmentStrategy:
    """定投策略"""
    
    def __init__(self, 
                 ahr999_calculator: AHR999Calculator,
                 exchange: BaseExchange,
                 config: Dict):
        """
        初始化定投策略
        
        Args:
            ahr999_calculator: AHR999计算器
            exchange: 交易所实例
            config: 配置字典
        """
        self.calculator = ahr999_calculator
        self.exchange = exchange
        self.config = config
        self.logger = get_logger()
        
        # 策略参数
        self.dca_threshold = config['strategy']['dca_threshold']
        self.bottom_threshold = config['strategy']['bottom_threshold']
        self.dca_amount = config['strategy']['dca_amount']
        self.bottom_amount = config['strategy']['bottom_amount']
        self.symbol = config['strategy']['symbol']
        self.min_balance = config['security']['min_balance']
        
        # 投资记录文件
        self.history_file = "logs/investment_history.json"
    
    def execute(self, dry_run: bool = False) -> Dict:
        """
        执行定投策略
        
        Args:
            dry_run: 是否为干运行（不实际交易）
            
        Returns:
            执行结果
        """
        try:
            self.logger.info("=" * 60)
            self.logger.info("Starting investment strategy execution")
            self.logger.info(f"Dry run mode: {dry_run}")
            
            # 检查今日是否已经执行过
            if not dry_run and self._has_invested_today():
                self.logger.warning("Already invested today, skipping")
                return {
                    'success': False,
                    'reason': 'already_invested_today'
                }
            
            # 计算AHR999
            ahr999, details = self.calculator.calculate(self.symbol)
            
            # 获取投资建议
            suggestion, amount = self.calculator.get_investment_suggestion(
                ahr999,
                self.dca_threshold,
                self.bottom_threshold
            )
            
            # 根据建议类型设置投资金额
            if suggestion == 'BOTTOM':
                invest_amount = self.bottom_amount
                reason = f"AHR999 ({ahr999:.4f}) < Bottom threshold ({self.bottom_threshold})"
            elif suggestion == 'DCA':
                invest_amount = self.dca_amount
                reason = f"AHR999 ({ahr999:.4f}) < DCA threshold ({self.dca_threshold})"
            else:
                invest_amount = 0
                reason = f"AHR999 ({ahr999:.4f}) >= DCA threshold ({self.dca_threshold})"
            
            # 记录决策
            self.logger.log_decision(ahr999, suggestion, reason)
            
            # 如果不需要投资
            if invest_amount == 0:
                self.logger.info("No investment needed at this time")
                return {
                    'success': True,
                    'action': 'HOLD',
                    'ahr999': ahr999,
                    'details': details,
                    'reason': reason
                }
            
            # 检查余额
            balance = self.exchange.get_balance("USDT")
            self.logger.info(f"Current USDT balance: {balance:.2f}")
            
            if balance < invest_amount:
                self.logger.warning(f"Insufficient balance: {balance:.2f} < {invest_amount}")
                return {
                    'success': False,
                    'reason': 'insufficient_balance',
                    'balance': balance,
                    'required': invest_amount
                }
            
            if balance < self.min_balance:
                self.logger.warning(f"Balance below minimum threshold: {balance:.2f} < {self.min_balance}")
                return {
                    'success': False,
                    'reason': 'below_min_balance',
                    'balance': balance
                }
            
            # 执行交易
            if dry_run:
                self.logger.info(
                    f"[DRY RUN] Would buy {self.symbol} with {invest_amount} USDT"
                )
                result = {
                    'success': True,
                    'action': suggestion,
                    'dry_run': True,
                    'ahr999': ahr999,
                    'details': details,
                    'invest_amount': invest_amount,
                    'reason': reason
                }
            else:
                # 实际执行交易
                self.logger.info(f"Executing market buy: {invest_amount} USDT")
                order = self.exchange.market_buy(self.symbol, invest_amount)
                
                # 记录交易
                current_price = details['current_price']
                btc_amount = invest_amount / current_price
                
                self.logger.log_trade(
                    exchange=self.config['exchange']['name'],
                    symbol=self.symbol,
                    amount=btc_amount,
                    price=current_price,
                    total=invest_amount,
                    ahr999=ahr999
                )
                
                # 保存投资记录
                self._save_investment_record({
                    'timestamp': datetime.now().isoformat(),
                    'ahr999': ahr999,
                    'action': suggestion,
                    'amount_usdt': invest_amount,
                    'amount_btc': btc_amount,
                    'price': current_price,
                    'order_id': order.get('id'),
                    'details': details
                })
                
                result = {
                    'success': True,
                    'action': suggestion,
                    'dry_run': False,
                    'ahr999': ahr999,
                    'details': details,
                    'invest_amount': invest_amount,
                    'btc_amount': btc_amount,
                    'order': order,
                    'reason': reason
                }
            
            self.logger.info("Investment strategy execution completed")
            self.logger.info("=" * 60)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing investment strategy: {str(e)}")
            raise
    
    def _has_invested_today(self) -> bool:
        """检查今天是否已经投资过"""
        if not os.path.exists(self.history_file):
            return False
        
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            
            today = datetime.now().date().isoformat()
            
            for record in history:
                record_date = datetime.fromisoformat(record['timestamp']).date().isoformat()
                if record_date == today:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Error checking investment history: {str(e)}")
            return False
    
    def _save_investment_record(self, record: Dict):
        """保存投资记录"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            
            # 读取现有记录
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
            else:
                history = []
            
            # 添加新记录
            history.append(record)
            
            # 保存
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2, default=str)
            
            self.logger.info("Investment record saved")
            
        except Exception as e:
            self.logger.error(f"Error saving investment record: {str(e)}")

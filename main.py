#!/usr/bin/env python3
"""
AHR999 Auto-Invest 主程序
基于AHR999指标的自动定投系统
"""
import argparse
import sys
from src.utils.config_loader import ConfigLoader
from src.utils.logger import get_logger
from src.data.price_fetcher import PriceFetcher
from src.data.ahr999_calculator import AHR999Calculator
from src.exchanges.exchange_factory import ExchangeFactory
from src.strategy.investment_strategy import InvestmentStrategy
from src.scheduler.investment_scheduler import InvestmentScheduler


def show_ahr999(config):
    """显示当前AHR999指标"""
    logger = get_logger(
        log_dir=config.get('logging.log_dir', 'logs'),
        log_level=config.get('logging.level', 'INFO')
    )
    
    logger.info("Fetching current AHR999 indicator...")
    
    # 创建价格获取器和AHR999计算器
    exchange_name = config.get('exchange.name', 'binance')
    symbol = config.get('strategy.symbol', 'BTC/USDT')
    ma_days = config.get('ahr999.ma_days', 200)
    
    price_fetcher = PriceFetcher(exchange_name)
    calculator = AHR999Calculator(price_fetcher, ma_days)
    
    # 计算AHR999
    ahr999, details = calculator.calculate(symbol)
    
    # 获取投资建议
    dca_threshold = config.get('strategy.dca_threshold', 1.0)
    bottom_threshold = config.get('strategy.bottom_threshold', 0.45)
    suggestion, amount = calculator.get_investment_suggestion(
        ahr999, dca_threshold, bottom_threshold
    )
    
    # 显示结果
    print("\n" + "=" * 60)
    print("AHR999 Indicator Report")
    print("=" * 60)
    print(f"Symbol:              {symbol}")
    print(f"Current Price:       ${details['current_price']:.2f}")
    print(f"MA{ma_days} Price:       ${details['ma_price']:.2f}")
    print(f"Fitted Price:        ${details['fitted_price']:.2f}")
    print(f"AHR999 Value:        {ahr999:.4f}")
    print("-" * 60)
    print(f"DCA Threshold:       {dca_threshold}")
    print(f"Bottom Threshold:    {bottom_threshold}")
    print("-" * 60)
    
    if suggestion == 'BOTTOM':
        print(f"💰 SUGGESTION:        Bottom Fishing - Invest {amount:.0f} USDT")
        print(f"   Reason:           AHR999 < {bottom_threshold}")
    elif suggestion == 'DCA':
        print(f"📊 SUGGESTION:        DCA - Invest {amount:.0f} USDT")
        print(f"   Reason:           AHR999 < {dca_threshold}")
    else:
        print(f"⏸️  SUGGESTION:        HOLD - No investment")
        print(f"   Reason:           AHR999 >= {dca_threshold}")
    
    print("=" * 60 + "\n")


def test_exchange(config, exchange_name):
    """测试交易所连接"""
    logger = get_logger(
        log_dir=config.get('logging.log_dir', 'logs'),
        log_level=config.get('logging.level', 'INFO')
    )
    
    logger.info(f"Testing {exchange_name} connection...")
    
    try:
        # 获取API凭证
        credentials = config.get_exchange_config(exchange_name)
        
        # 创建交易所实例
        exchange = ExchangeFactory.create_exchange(exchange_name, credentials)
        
        # 测试连接
        exchange.connect()
        
        # 获取余额
        balance = exchange.get_balance("USDT")
        
        # 获取BTC价格
        symbol = config.get('strategy.symbol', 'BTC/USDT')
        ticker = exchange.get_ticker(symbol)
        price = ticker['last']
        
        print("\n" + "=" * 60)
        print(f"{exchange_name.upper()} Connection Test")
        print("=" * 60)
        print(f"✅ Status:           Connected")
        print(f"💰 USDT Balance:     {balance:.2f}")
        print(f"📈 {symbol} Price:    ${price:.2f}")
        print("=" * 60 + "\n")
        
        logger.info(f"{exchange_name} connection test successful")
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"{exchange_name.upper()} Connection Test")
        print("=" * 60)
        print(f"❌ Status:           Failed")
        print(f"   Error:            {str(e)}")
        print("=" * 60 + "\n")
        
        logger.error(f"{exchange_name} connection test failed: {str(e)}")
        return False


def validate_config(config):
    """验证配置"""
    logger = get_logger(
        log_dir=config.get('logging.log_dir', 'logs'),
        log_level=config.get('logging.level', 'INFO')
    )
    
    logger.info("Validating configuration...")
    
    try:
        config.validate()
        print("\n✅ Configuration validation passed!\n")
        logger.info("Configuration validation successful")
        return True
    except Exception as e:
        print(f"\n❌ Configuration validation failed: {str(e)}\n")
        logger.error(f"Configuration validation failed: {str(e)}")
        return False


def execute_strategy(config, dry_run=False):
    """执行投资策略"""
    logger = get_logger(
        log_dir=config.get('logging.log_dir', 'logs'),
        log_level=config.get('logging.level', 'INFO')
    )
    
    # 创建组件
    exchange_name = config.get('exchange.name')
    credentials = config.get_exchange_config(exchange_name)
    exchange = ExchangeFactory.create_exchange(exchange_name, credentials)
    exchange.connect()
    
    price_fetcher = PriceFetcher(exchange_name)
    ma_days = config.get('ahr999.ma_days', 200)
    calculator = AHR999Calculator(price_fetcher, ma_days)
    
    strategy = InvestmentStrategy(calculator, exchange, config.config)
    
    # 执行策略
    result = strategy.execute(dry_run=dry_run)
    
    return result


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='AHR999 Auto-Invest - Automated Bitcoin DCA based on AHR999 indicator'
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--show-ahr999',
        action='store_true',
        help='Show current AHR999 indicator value'
    )
    
    parser.add_argument(
        '--test-exchange',
        choices=['binance', 'okx', 'bitget'],
        help='Test exchange API connection'
    )
    
    parser.add_argument(
        '--validate-config',
        action='store_true',
        help='Validate configuration file'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run in dry-run mode (no actual trading)'
    )
    
    parser.add_argument(
        '--execute-once',
        action='store_true',
        help='Execute investment strategy once and exit'
    )
    
    args = parser.parse_args()
    
    try:
        # 加载配置
        config_loader = ConfigLoader(args.config)
        config_loader.load()
        
        # 根据命令行参数执行不同操作
        if args.show_ahr999:
            show_ahr999(config_loader)
            
        elif args.test_exchange:
            test_exchange(config_loader, args.test_exchange)
            
        elif args.validate_config:
            validate_config(config_loader)
            
        elif args.execute_once:
            logger = get_logger(
                log_dir=config_loader.get('logging.log_dir', 'logs'),
                log_level=config_loader.get('logging.level', 'INFO')
            )
            logger.info("Executing investment strategy once...")
            result = execute_strategy(config_loader, dry_run=args.dry_run)
            logger.info(f"Execution result: {result}")
            
        else:
            # 启动定时任务
            logger = get_logger(
                log_dir=config_loader.get('logging.log_dir', 'logs'),
                log_level=config_loader.get('logging.level', 'INFO')
            )
            
            logger.info("Starting AHR999 Auto-Invest System...")
            
            # 创建调度器
            hour = config_loader.get('scheduler.hour', 0)
            minute = config_loader.get('scheduler.minute', 0)
            timezone = config_loader.get('scheduler.timezone', 'Asia/Shanghai')
            
            def execute_task():
                execute_strategy(config_loader, dry_run=args.dry_run)
            
            scheduler = InvestmentScheduler(
                execute_func=execute_task,
                hour=hour,
                minute=minute,
                timezone=timezone
            )
            
            scheduler.schedule_daily()
            scheduler.run_forever()
            
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

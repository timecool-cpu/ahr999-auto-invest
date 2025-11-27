#!/usr/bin/env python3
"""
AHR999诊断工具
对比不同时期的AHR999值，找出计算差异
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from src.data.price_fetcher import PriceFetcher
from src.utils.logger import get_logger


def calculate_ma(prices, window=200):
    """计算移动平均"""
    if len(prices) < window:
        return [np.nan] * len(prices)
    
    ma = []
    for i in range(len(prices)):
        if i < window - 1:
            ma.append(np.nan)
        else:
            ma.append(np.mean(prices[i-window+1:i+1]))
    return ma


def calculate_fitted_price_method1(dates, prices):
    """方法1: 基于全部历史数据的回归"""
    genesis_date = datetime(2009, 1, 3)
    
    days_list = []
    log_prices = []
    
    for date, price in zip(dates, prices):
        days_since_genesis = (date - genesis_date).days
        if price > 0:
            days_list.append(days_since_genesis)
            log_prices.append(np.log10(price))
    
    coeffs = np.polyfit(days_list, log_prices, 1)
    a, b = coeffs[0], coeffs[1]
    
    fitted_prices = []
    for date in dates:
        days_since_genesis = (date - genesis_date).days
        fitted_price = 10 ** (a * days_since_genesis + b)
        fitted_prices.append(fitted_price)
    
    return fitted_prices, a, b


def calculate_fitted_price_method2(dates):
    """
    方法2: 使用固定参数（参考AHR999原始定义）
    基于比特币历史长期趋势的指数拟合
    """
    genesis_date = datetime(2009, 1, 3)
    
    # 使用更接近实际的参数
    # 参考：10^(2.5 + 5.84 * log10(days/365.25))
    fitted_prices = []
    for date in dates:
        days_since_genesis = (date - genesis_date).days
        years = days_since_genesis / 365.25
        
        # 方法2a: 简单指数模型
        if years > 0:
            fitted_price = 10 ** (2.5 + 5.84 * np.log10(years))
        else:
            fitted_price = 1
        
        fitted_prices.append(fitted_price)
    
    return fitted_prices


def main():
    logger = get_logger()
    
    # 获取历史数据
    fetcher = PriceFetcher("binance")
    days = 1200
    historical_data = fetcher.get_historical_prices("BTC/USDT", days=days)
    
    dates = [d[0] for d in historical_data]
    prices = [d[1] for d in historical_data]
    
    logger.info(f"Analyzing {len(dates)} days from {dates[0]} to {dates[-1]}")
    
    # 计算200日MA
    ma_200 = calculate_ma(prices, 200)
    
    # 方法1: 线性回归
    fitted_1, a1, b1 = calculate_fitted_price_method1(dates, prices)
    logger.info(f"Method 1 (Linear regression): a={a1:.8f}, b={b1:.4f}")
    
    # 方法2: 固定公式
    fitted_2 = calculate_fitted_price_method2(dates)
    logger.info(f"Method 2 (Power law)")
    
    # 计算两种方法的AHR999
    ahr999_method1 = []
    ahr999_method2 = []
    
    for i in range(len(prices)):
        if np.isnan(ma_200[i]):
            ahr999_method1.append(np.nan)
            ahr999_method2.append(np.nan)
        else:
            ahr999_1 = (prices[i] / ma_200[i]) * (prices[i] / fitted_1[i])
            ahr999_2 = (prices[i] / ma_200[i]) * (prices[i] / fitted_2[i])
            ahr999_method1.append(ahr999_1)
            ahr999_method2.append(ahr999_2)
    
    # 找出2023年5-9月的数据
    target_start = datetime(2023, 5, 1)
    target_end = datetime(2023, 10, 1)
    
    print("\n" + "="*70)
    print("2023年5-9月期间的AHR999值对比")
    print("="*70)
    print(f"{'日期':<12} {'价格':<10} {'MA200':<10} {'拟合1':<10} {'AHR999-1':<10} {'拟合2':<10} {'AHR999-2':<10}")
    print("-"*70)
    
    for i, date in enumerate(dates):
        if target_start <= date <= target_end and not np.isnan(ahr999_method1[i]):
            print(f"{date.strftime('%Y-%m-%d'):<12} "
                  f"${prices[i]:<9.0f} "
                  f"${ma_200[i]:<9.0f} "
                  f"${fitted_1[i]:<9.0f} "
                  f"{ahr999_method1[i]:<10.4f} "
                  f"${fitted_2[i]:<9.0f} "
                  f"{ahr999_method2[i]:<10.4f}")
    
    # 创建对比图
    fig, axes = plt.subplots(3, 1, figsize=(16, 14))
    
    # 价格对比
    ax1 = axes[0]
    ax1.plot(dates, prices, 'b-', label='BTC价格', alpha=0.7)
    ax1.plot(dates, ma_200, 'orange', label='200日MA', alpha=0.7)
    ax1.plot(dates, fitted_1, 'g--', label='拟合价格-方法1', alpha=0.7)
    ax1.plot(dates, fitted_2, 'r--', label='拟合价格-方法2', alpha=0.7)
    ax1.set_ylabel('价格 (USD)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_title('价格对比')
    
    # AHR999对比 - 方法1
    ax2 = axes[1]
    ax2.plot(dates, ahr999_method1, 'b-', label='AHR999-方法1（线性回归）', alpha=0.8)
    ax2.axhline(y=1.0, color='green', linestyle='-', alpha=0.5, label='定投线')
    ax2.axhline(y=0.45, color='red', linestyle='-', alpha=0.5, label='抄底线')
    ax2.fill_between(dates, 0, ahr999_method1, 
                     where=[v <= 0.45 if not np.isnan(v) else False for v in ahr999_method1],
                     color='red', alpha=0.2)
    ax2.set_ylabel('AHR999')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_title('AHR999 - 方法1（当前使用）')
    
    # AHR999对比 - 方法2
    ax3 = axes[2]
    ax3.plot(dates, ahr999_method2, 'r-', label='AHR999-方法2（幂律模型）', alpha=0.8)
    ax3.axhline(y=1.0, color='green', linestyle='-', alpha=0.5, label='定投线')
    ax3.axhline(y=0.45, color='red', linestyle='-', alpha=0.5, label='抄底线')
    ax3.fill_between(dates, 0, ahr999_method2,
                     where=[v <= 0.45 if not np.isnan(v) else False for v in ahr999_method2],
                     color='red', alpha=0.2)
    ax3.set_ylabel('AHR999')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_title('AHR999 - 方法2（幂律模型）')
    ax3.set_xlabel('日期')
    
    plt.tight_layout()
    plt.savefig('ahr999_diagnostic.png', dpi=300, bbox_inches='tight')
    logger.info("Diagnostic chart saved to ahr999_diagnostic.png")
    
    print("\n✅ 诊断完成！图表已保存为: ahr999_diagnostic.png")


if __name__ == "__main__":
    main()

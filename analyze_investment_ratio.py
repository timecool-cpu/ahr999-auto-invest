#!/usr/bin/env python3
"""
分析定投和抄底金额比例的合理性
基于历史AHR999数据分析不同区间的出现频率和后续收益
"""
import numpy as np
from datetime import datetime, timedelta
from src.data.price_fetcher import PriceFetcher
from src.utils.logger import get_logger

def analyze_ahr999_distribution():
    """分析AHR999在不同区间的分布"""
    logger = get_logger()
    fetcher = PriceFetcher("binance")
    
    # 获取3年历史数据
    days = 1200
    historical_data = fetcher.get_historical_prices("BTC/USDT", days=days)
    
    dates = [d[0] for d in historical_data]
    prices = [d[1] for d in historical_data]
    
    logger.info(f"Analyzing {len(dates)} days from {dates[0]} to {dates[-1]}")
    
    # 计算AHR999
    genesis_date = datetime(2009, 1, 3)
    ahr999_values = []
    valid_dates = []
    valid_prices = []
    
    for i in range(200, len(prices)):  # 需要200天数据计算MA
        # 200日MA
        ma200 = np.mean(prices[i-200:i])
        
        # 拟合价格
        days_since_genesis = (dates[i] - genesis_date).days
        fitted_price = 10 ** (5.84 * np.log10(days_since_genesis) - 17.01)
        
        # AHR999
        ahr999 = (prices[i] / ma200) * (prices[i] / fitted_price)
        
        ahr999_values.append(ahr999)
        valid_dates.append(dates[i])
        valid_prices.append(prices[i])
    
    # 统计不同区间的出现频率
    bottom_zone = sum(1 for v in ahr999_values if v < 0.45)
    dca_zone = sum(1 for v in ahr999_values if 0.45 <= v < 1.2)
    hold_zone = sum(1 for v in ahr999_values if v >= 1.2)
    total = len(ahr999_values)
    
    print("\n" + "="*70)
    print("AHR999 历史分布分析（近3年）")
    print("="*70)
    print(f"分析期间: {valid_dates[0].strftime('%Y-%m-%d')} 至 {valid_dates[-1].strftime('%Y-%m-%d')}")
    print(f"总天数: {total} 天")
    print("-"*70)
    print(f"{'区间':<15} {'天数':>8} {'占比':>10} {'说明'}")
    print("-"*70)
    print(f"{'抄底区 (<0.45)':<15} {bottom_zone:>8} {bottom_zone/total*100:>9.1f}% {'极度低估，大额买入'}")
    print(f"{'定投区 [0.45,1.2)':<15} {dca_zone:>8} {dca_zone/total*100:>9.1f}% {'合理区间，定期买入'}")
    print(f"{'观望区 (>=1.2)':<15} {hold_zone:>8} {hold_zone/total*100:>9.1f}% {'高估区间，不建议买入'}")
    print("="*70)
    
    # 分析后续收益（30天、90天、180天）
    print("\n" + "="*70)
    print("不同区间买入后的平均收益分析")
    print("="*70)
    
    periods = [30, 90, 180]
    
    for period in periods:
        print(f"\n持有 {period} 天后的平均收益:")
        print("-"*70)
        
        bottom_returns = []
        dca_returns = []
        hold_returns = []
        
        for i in range(len(ahr999_values) - period):
            buy_price = valid_prices[i]
            sell_price = valid_prices[i + period]
            return_pct = (sell_price - buy_price) / buy_price * 100
            
            if ahr999_values[i] < 0.45:
                bottom_returns.append(return_pct)
            elif ahr999_values[i] < 1.2:
                dca_returns.append(return_pct)
            else:
                hold_returns.append(return_pct)
        
        if bottom_returns:
            avg_bottom = np.mean(bottom_returns)
            med_bottom = np.median(bottom_returns)
            print(f"  抄底区买入:   平均收益 {avg_bottom:>6.1f}%  |  中位数 {med_bottom:>6.1f}%")
        
        if dca_returns:
            avg_dca = np.mean(dca_returns)
            med_dca = np.median(dca_returns)
            print(f"  定投区买入:   平均收益 {avg_dca:>6.1f}%  |  中位数 {med_dca:>6.1f}%")
        
        if hold_returns:
            avg_hold = np.mean(hold_returns)
            med_hold = np.median(hold_returns)
            print(f"  观望区买入:   平均收益 {avg_hold:>6.1f}%  |  中位数 {med_hold:>6.1f}%")
    
    # 计算合理的投资比例建议
    print("\n" + "="*70)
    print("投资金额比例建议")
    print("="*70)
    
    # 基于频率和收益的综合分析
    bottom_freq = bottom_zone / total
    dca_freq = dca_zone / total
    
    # 计算180天收益比
    if bottom_returns and dca_returns:
        avg_bottom_180 = np.mean([r for i, r in enumerate([(valid_prices[i+180] - valid_prices[i])/valid_prices[i]*100 
                                                            for i in range(len(ahr999_values)-180)]) 
                                  if i < len(ahr999_values)-180 and ahr999_values[i] < 0.45])
        avg_dca_180 = np.mean([r for i, r in enumerate([(valid_prices[i+180] - valid_prices[i])/valid_prices[i]*100 
                                                         for i in range(len(ahr999_values)-180)]) 
                               if i < len(ahr999_values)-180 and 0.45 <= ahr999_values[i] < 1.2])
        
        # 收益倍数比
        if avg_dca_180 > 0:
            return_ratio = avg_bottom_180 / avg_dca_180
        else:
            return_ratio = 2.0  # 默认
    else:
        return_ratio = 2.0
    
    # 频率倒数比（稀缺性）
    if bottom_freq > 0 and dca_freq > 0:
        scarcity_ratio = dca_freq / bottom_freq
    else:
        scarcity_ratio = 2.0
    
    # 综合建议比例
    suggested_ratio = (return_ratio + scarcity_ratio) / 2
    
    # 以100U为基准
    base_dca = 100
    suggested_bottom = base_dca * suggested_ratio
    
    print(f"\n分析依据:")
    print(f"  1. 抄底区出现频率: {bottom_freq*100:.1f}% (稀缺性: {scarcity_ratio:.1f}x)")
    print(f"  2. 定投区出现频率: {dca_freq*100:.1f}%")
    if bottom_returns and dca_returns:
        print(f"  3. 抄底区180天平均收益: {avg_bottom_180:.1f}%")
        print(f"  4. 定投区180天平均收益: {avg_dca_180:.1f}%")
        print(f"  5. 收益倍数比: {return_ratio:.1f}x")
    
    print(f"\n建议配置:")
    print(f"  定投金额 (0.45 ≤ AHR999 < 1.2):  {base_dca} USDT")
    print(f"  抄底金额 (AHR999 < 0.45):        {suggested_bottom:.0f} USDT")
    print(f"  比例: 1 : {suggested_ratio:.1f}")
    
    print(f"\n说明:")
    print(f"  - 抄底区更稀缺（出现频率仅{bottom_freq*100:.1f}%），应加大投入")
    print(f"  - 抄底区后续收益通常更高，风险收益比更优")
    print(f"  - 建议比例综合考虑了稀缺性和收益率")
    
    # 给出不同风险偏好的建议
    print(f"\n不同风险偏好建议:")
    print(f"  保守型:   定投100U / 抄底150U  (比例 1:1.5)")
    print(f"  平衡型:   定投100U / 抄底{suggested_bottom:.0f}U  (比例 1:{suggested_ratio:.1f})")
    print(f"  激进型:   定投100U / 抄底{suggested_bottom*1.5:.0f}U  (比例 1:{suggested_ratio*1.5:.1f})")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    analyze_ahr999_distribution()

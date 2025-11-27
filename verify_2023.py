#!/usr/bin/env python3
from datetime import datetime
import numpy as np
from src.data.price_fetcher import PriceFetcher

genesis_date = datetime(2009, 1, 3)
fetcher = PriceFetcher('binance')
data = fetcher.get_historical_prices('BTC/USDT', days=1200)

print('2023年5-9月 AHR999值验证:')
print('='*80)
print(f"{'日期':<12} {'价格':>10} {'MA200':>10} {'拟合价格':>12} {'AHR999':>10} {'状态':<10}")
print('-'*80)

target_start = datetime(2023, 5, 1)
target_end = datetime(2023, 10, 1)

for i, (date, price) in enumerate(data):
    if i >= 200:
        ma200 = np.mean([p for _, p in data[i-200:i]])
        days = (date - genesis_date).days
        fitted = 10 ** (5.84 * np.log10(days) - 17.01) if days > 0 else 1
        ahr999 = (price / ma200) * (price / fitted)
        
        if target_start <= date <= target_end and date.day == 1:
            status = '抄底' if ahr999 < 0.45 else ('定投' if ahr999 < 1.2 else '观望')
            print(f"{date.strftime('%Y-%m-%d'):<12} ${price:>9.0f} ${ma200:>9.0f} ${fitted:>11.0f} {ahr999:>10.4f} {status:<10}")

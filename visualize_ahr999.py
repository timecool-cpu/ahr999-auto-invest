"""
AHR999指标可视化
生成AHR999历史趋势图表
"""
import sys
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
from src.data.price_fetcher import PriceFetcher
from src.utils.logger import get_logger

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


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


def calculate_fitted_prices_from_data(dates, prices):
    """
    使用AHR999标准公式计算拟合价格
    标准公式: Price = 10^(5.84 * log10(coin_age_days) - 17.01)
    """
    genesis_date = datetime(2009, 1, 3)
    
    fitted_prices = []
    for date in dates:
        days_since_genesis = (date - genesis_date).days
        
        # AHR999标准公式
        if days_since_genesis > 0:
            fitted_price = 10 ** (5.84 * np.log10(days_since_genesis) - 17.01)
        else:
            fitted_price = 1
        
        fitted_prices.append(fitted_price)
    
    return fitted_prices


def main():
    logger = get_logger()
    logger.info("Fetching historical data for visualization...")
    
    # 获取历史数据（3年+的数据用于可视化）
    fetcher = PriceFetcher("binance")
    days = 1200  # 获取3年以上数据以便有足够的200日MA
    historical_data = fetcher.get_historical_prices("BTC/USDT", days=days)
    
    # 提取数据
    dates = [d[0] for d in historical_data]
    prices = [d[1] for d in historical_data]
    
    logger.info(f"Fetched {len(dates)} days of data from {dates[0]} to {dates[-1]}")
    
    # 计算200日移动平均
    ma_200 = calculate_ma(prices, 200)
    
    # 计算拟合价格（使用AHR999标准公式）
    fitted_prices = calculate_fitted_prices_from_data(dates, prices)
    
    logger.info(f"Using standard AHR999 fitted price formula: 10^(5.84*log10(days)-17.01)")
    
    # 计算AHR999
    ahr999_values = []
    for i in range(len(prices)):
        if np.isnan(ma_200[i]):
            ahr999_values.append(np.nan)
        else:
            ahr999 = (prices[i] / ma_200[i]) * (prices[i] / fitted_prices[i])
            ahr999_values.append(ahr999)
    
    # 显示最近三年的数据（约1095天）
    display_days = min(1095, len(dates))
    dates_display = dates[-display_days:]
    prices_display = prices[-display_days:]
    ma_200_display = ma_200[-display_days:]
    fitted_prices_display = fitted_prices[-display_days:]
    ahr999_values_display = ahr999_values[-display_days:]
    
    # 创建图表（调整比例，让AHR999图更显眼）
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), 
                                    gridspec_kw={'height_ratios': [1, 2]})
    
    # 上半部分：价格图
    ax1_right = ax1.twinx()
    
    # 绘制价格线
    line1 = ax1.plot(dates_display, prices_display, 'b-', linewidth=1.5, 
                     label='BTC价格', alpha=0.8)
    
    # 绘制200日定投成本
    line2 = ax1.plot(dates_display, ma_200_display, 'orange', linewidth=2, 
                     label='200日定投成本', alpha=0.8)
    
    # 绘制拟合价格
    line3 = ax1.plot(dates_display, fitted_prices_display, 'green', linewidth=2, 
                     label='拟合价格', alpha=0.7, linestyle='--')
    
    # 设置价格轴
    ax1.set_ylabel('价格 (USDT)', fontsize=12, fontweight='bold')
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax1.grid(True, alpha=0.3)
    
    # 下半部分：AHR999指标
    ax2.plot(dates_display, ahr999_values_display, 'b-', linewidth=2, 
             label='AHR999指数', alpha=0.8)
    
    # 添加阈值线
    ax2.axhline(y=1.0, color='green', linestyle='-', linewidth=1.5, 
                label='定投线 (1.0)', alpha=0.7)
    ax2.axhline(y=0.45, color='red', linestyle='-', linewidth=1.5, 
                label='抄底线 (0.45)', alpha=0.7)
    
    # 填充区域
    ax2.fill_between(dates_display, 0, ahr999_values_display, 
                     where=[v <= 0.45 if not np.isnan(v) else False for v in ahr999_values_display],
                     color='red', alpha=0.2, label='抄底区域')
    ax2.fill_between(dates_display, 0.45, ahr999_values_display,
                     where=[(v > 0.45 and v <= 1.0) if not np.isnan(v) else False for v in ahr999_values_display],
                     color='yellow', alpha=0.2, label='定投区域')
    ax2.fill_between(dates_display, 1.0, ahr999_values_display,
                     where=[v > 1.0 if not np.isnan(v) else False for v in ahr999_values_display],
                     color='purple', alpha=0.15, label='观望区域')
    
    # 设置AHR999轴
    ax2.set_ylabel('AHR999指数', fontsize=12, fontweight='bold')
    ax2.set_xlabel('日期', fontsize=12, fontweight='bold')
    ax2.set_ylim(0, max([v for v in ahr999_values_display if not np.isnan(v)]) * 1.1)
    ax2.grid(True, alpha=0.3)
    
    # 格式化x轴日期
    for ax in [ax1, ax2]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 添加图例
    ax1.legend(loc='upper left', fontsize=10)
    ax2.legend(loc='upper left', fontsize=10)
    
    # 添加标题
    current_ahr999 = ahr999_values_display[-1]
    current_price = prices_display[-1]
    fig.suptitle(f'比特币 AHR999 指标\n当前价格: ${current_price:,.2f} | 当前AHR999: {current_ahr999:.4f}', 
                 fontsize=16, fontweight='bold')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图表
    output_file = 'ahr999_chart.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    logger.info(f"Chart saved to {output_file}")
    
    # 不显示图表窗口，直接保存
    # plt.show()
    
    print(f"\n✅ 图表已生成并保存为: {output_file}")
    print(f"\n当前数据:")
    print(f"  BTC价格: ${current_price:,.2f}")
    print(f"  200日定投成本: ${ma_200_display[-1]:,.2f}")
    print(f"  拟合价格: ${fitted_prices_display[-1]:,.2f}")
    print(f"  AHR999指数: {current_ahr999:.4f}")
    
    if current_ahr999 < 0.45:
        print(f"  💰 建议: 抄底 - 定投 200 USDT")
    elif current_ahr999 < 1.0:
        print(f"  📊 建议: 定投 - 定投 100 USDT")
    else:
        print(f"  ⏸️  建议: 观望 - 不定投")


if __name__ == "__main__":
    main()

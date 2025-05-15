


import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from curl_cffi import requests

# Step 1: 创建模拟浏览器 session（绕过 yfinance 限流）
session = requests.Session(impersonate="chrome")

def fetch_soxl_history(ticker, start_date, end_date):
    tkr = yf.Ticker(ticker, session=session)
    df = tkr.history(start=start_date, end=end_date)
    df = df[['Close']].dropna()
    df.index = df.index.tz_localize(None)
    df = df.groupby(df.index.date).last()
    df.index = pd.to_datetime(df.index)
    return df

# Step 2: 拉取数据并构造条件信号
df = fetch_soxl_history("SOXL", "2001-01-01", "2025-05-13")
df['Return'] = df['Close'].pct_change()
df['2D_Return'] = df['Close'].pct_change(2)

# Step 3: 筛选信号日：连续两天上涨≥26%
signal_days = df[df['2D_Return'] >= 0.26].index

# Step 4: 计算未来3~7天累计收益
future_returns = {n: [] for n in range(3, 8)}
for day in signal_days:
    for n in range(3, 8):
        try:
            future_period = df.loc[day + pd.Timedelta(days=1): day + pd.Timedelta(days=n), 'Return']
            cumulative = future_period.sum()
            future_returns[n].append(cumulative)
        except KeyError:
            continue

# Step 5: 打印统计结果 + 绘图可视化
results = {}
for n, values in future_returns.items():
    series = pd.Series(values)
    mean_val = series.mean()
    var_5 = series.quantile(0.05)
    skewness = series.skew()
    left_prob = (series < mean_val).mean()
    right_prob = (series >= mean_val).mean()

    # 保存结果
    results[n] = {
        'mean': mean_val,
        'VaR_5%': var_5,
        'skew': skewness,
        'left_prob': left_prob,
        'right_prob': right_prob
    }

    # 可视化分布
    plt.figure(figsize=(10, 6))
    sns.histplot(series, bins=30, kde=True, color='skyblue', edgecolor='black')
    plt.axvline(var_5, color='orange', linestyle='--', label=f'VaR 5% = {round(var_5, 4)}')
    plt.axvline(0, color='red', linestyle='--', label='Zero Return')
    plt.title(f'Cumulative Return Distribution Over Next {n} Days (Given Prior 2-Day Gain ≥ 26%)')
    plt.xlabel(f'Cumulative Return Over Next {n} Days')

    plt.ylabel('频数')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Step 6: 输出总表
results_df = pd.DataFrame(results).T
print("\n📊 条件收益统计：\n")
print(results_df)






####条件概率

import yfinance as yf
import pandas as pd
from curl_cffi import requests

# 模拟 Chrome 浏览器请求，绕过 yfinance 限流
session = requests.Session(impersonate="chrome")

def fetch_soxl_history(ticker, start_date, end_date):
    tkr = yf.Ticker(ticker, session=session)
    df = tkr.history(start=start_date, end=end_date)
    df = df[['Close']].dropna()
    df.index = df.index.tz_localize(None)
    df = df.groupby(df.index.date).last()
    df.index = pd.to_datetime(df.index)
    return df

# 获取数据
df = fetch_soxl_history("SOXL", "2001-01-01", "2025-05-13")

# 计算日收益率
df['Return'] = df['Close'].pct_change()

# 识别单日涨幅 ≥18% 的日期
signal_days = df[df['Return'] >= 0.18].index

# 初始化计数器
count_gt_3 = 0
count_lt_neg1 = 0
count_gt_5 = 0
valid_cases = 0

# 遍历所有信号日
for day in signal_days:
    try:
        next_7_days = df.loc[day + pd.Timedelta(days=1): day + pd.Timedelta(days=7), 'Return']
        cumulative_return = next_7_days.sum()
        valid_cases += 1

        if cumulative_return > 0.03:
            count_gt_3 += 1
        if cumulative_return < -0.03:
            count_lt_neg1 += 1
        if cumulative_return > 0.05:
            count_gt_5 += 1

    except KeyError:
        continue  # 忽略未来数据不足的日期

# 输出结果
print("未来7日收益 > 3% 的概率：", count_gt_3 / valid_cases)
print("未来7日收益 < -3% 的概率：", count_lt_neg1 / valid_cases)
print("未来7日收益 > 5% 的概率：", count_gt_5 / valid_cases)



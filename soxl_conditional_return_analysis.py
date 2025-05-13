

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








import matplotlib.pyplot as plt
import seaborn as sns

# 收集所有信号日之后7天的累计收益
cumulative_returns = []

for day in signal_days:
    try:
        next_7_days = df.loc[day + pd.Timedelta(days=1): day + pd.Timedelta(days=7), 'Return']
        cumulative_return = next_7_days.sum()
        cumulative_returns.append(cumulative_return)
    except KeyError:
        continue

# 转为 Series
cumulative_returns = pd.Series(cumulative_returns)

# 绘图

# 计算均值
mean_return = cumulative_returns.mean()

# 左边：小于均值的比例
left_prob = (cumulative_returns < mean_return).mean()

# 右边：大于等于均值的比例
right_prob = (cumulative_returns >= mean_return).mean()

# 打印结果
print("均值：", round(mean_return, 4))
print("左边（<均值）概率：", round(left_prob, 4))
print("右边（≥均值）概率：", round(right_prob, 4))

# 偏态判断
if cumulative_returns.skew() > 0:
    print("分布偏态：右偏（右尾更长）")
elif cumulative_returns.skew() < 0:
    print("分布偏态：左偏（左尾更长）")
else:
    print("分布偏态：大致对称")
# 计算VaR 5%
var_5 = cumulative_returns.quantile(0.05)

# 打印VaR值
print("VaR 5%（未来7日收益分布的5%分位数）：", round(var_5, 4))

# 可视化：添加 VaR 线到直方图
plt.figure(figsize=(10, 6))
sns.histplot(cumulative_returns, bins=30, kde=True, color='skyblue', edgecolor='black')
plt.axvline(var_5, color='orange', linestyle='--', label=f'VaR 5% = {round(var_5, 4)}')
plt.axvline(0, color='red', linestyle='--', label='Zero Return')
plt.title('未来7日累计收益分布（含VaR 5%）')
plt.xlabel('未来7日累计收益')
plt.ylabel('频数')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

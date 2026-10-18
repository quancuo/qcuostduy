from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

# 行：第 1～5 天 origin data
# 列：Python、Git、数学
minutes = np.array([
    [20, 45, 30],
    [35, 20, 50],
    [60, 30, 25],
    [15, 40, 45],
    [30, 55, 20],
], dtype=np.int64)

print(minutes)
print("shape =", minutes.shape)

# 把同一天的三个主题加起来。
daily_total = minutes.sum(axis=1)
print("daily_total =", daily_total)
print("daily_total shape =", daily_total.shape)

#这次要把同一个主题在五天中的记录汇总起来 means and totals
topic_total = minutes.sum(axis=0)
print("topic_total =", topic_total)
print("topic_total shape =", topic_total.shape)

topic_means = minutes.mean(axis=0)
print("topic_means =", topic_means)
print("topic_means shape =", topic_means.shape)


#每列减去该列均值 result shape = (5, 3)----broadcasting is working
centered = minutes - topic_means
print("centered =", centered)
print("centered shape =", centered.shape)
print("centered dtype =", centered.dtype)

##daily photosynthesis
days =np.arange(1, 6)
print("横坐标 =", days)
print("横坐标 shape =", days.shape)
print("纵坐标 shape =", daily_total.shape)

###########
# 创建画布和一个绘图区
# figsize：画布尺寸，单位是英寸
fig, ax = plt.subplots(figsize=(7, 4))

# plot：画折线
# marker="o"：在每个数据点画一个圆形标记
ax.plot(days, daily_total, marker='o')

# 图中文字
ax.set_title("Daily Total Minutes")
ax.set_xlabel("Day")
ax.set_ylabel("Total Minutes")

# 横轴刻度为第 1～5 天 # 纵轴范围为 0～130 分钟
ax.set_xticks(days)
ax.set_ylim(0,130)

# 显示网格；alpha 控制不透明度
ax.grid(True,alpha=0.3)

# 调整布局，让标题和坐标说明排列完整
fig.tight_layout()

# 将图片保存在 main.py 所在的文件夹 # dpi：每英寸点数，这里使用 150
output_path = Path(__file__).parent / "daily_total_minutes.png"
fig.savefig(output_path,dpi=150)

print(f"Saved figure to {output_path}")



##practice A
hours = minutes / 60
print("hours =", hours)
print("hours shape =", hours.shape)

#practice B
# : 表示选择所有行，也就是所有天
# 0 表示第 1 列，也就是 Python 主题

python_minutes = minutes[:,0]
print("Python 每日学习分钟数：", python_minutes)
print("形状：", python_minutes.shape)

# arange(1, 6)：从 1 开始，到 6 之前结束，得到第 1～5 天
days = np.arange(1, 6)
# 创建画布和绘图区
fig_python, ax_python = plt.subplots(figsize=(7, 4))

# 横坐标是天数，纵坐标是对应的 Python 学习分钟数
# marker="o"：在每个数据点画一个圆点
ax_python.plot(days, python_minutes, marker="o")

ax_python.set_title("Daily Python study time")
ax_python.set_xlabel("Day")
ax_python.set_ylabel("Study time (minutes)")

# 横轴只标出第 1～5 天
ax_python.set_xticks(days)

# 纵轴显示范围：0～70 分钟
ax_python.set_ylim(0, 70)

# 显示网格；alpha 表示透明程度
ax_python.grid(True, alpha=0.3)

# 自动调整布局，给标题和坐标说明留出空间
fig_python.tight_layout()

# 将图片保存在当前代码文件所在的文件夹
python_path = Path(__file__).resolve().parent / "python_minutes.png"

# dpi 表示图片分辨率，这里使用 150
fig_python.savefig(python_path, dpi=150)

print("图片已保存到：", python_path)








#practice C
bonus =np.array([5, 10, 0])
minutes_b =minutes + bonus
print (minutes_b)
print (minutes_b.shape)

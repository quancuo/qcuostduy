# D9：Pandas 索引、条件筛选和排序

日期：2026-10-20。今天使用虚构资产数据练习，不涉及真实市场判断。

## 启动与文件

在 PowerShell 运行：

```powershell
& "D:\Learning\Start-Jupyter.cmd"
```

& 是 PowerShell 的调用操作符。浏览器打开后进入 d9，选择 practice.ipynb；
内核使用 Python (D Learning)。Shift + Enter 运行单元格，Ctrl + S 保存。
从上往下执行。reference.ipynb 是中文注释参考版，notes.md 是问答题。
第 217 题参考代码另存于 D:/Learning/study/cs61A/217.py。

## 知识点

- index 是索引标签，位置是当前排列中从 0 开始的顺序。loc 按标签，iloc 按位置。
- set_index("record_id") 用已有列作索引，返回新表；record_id 不是特殊列名。
- 比较条件得到布尔 Series，用 df.loc[条件] 保留条件为 True 的行。
- & 表示逐行并且；| 表示逐行或者；~ 表示取反。组合比较条件分别加括号。
- sort_values 按列值排序；sort_index 按索引标签排序；reset_index 重新编号。
- 排序后标签跟随记录移动；reset_index() 默认把旧索引保存成列，drop=True 则丢掉旧标签。
- 上述操作默认用新变量接收；不会因为调用后打印了结果就自动改写原表。

## 数据

data/prices.csv 共 8 行 5 列：record_id（编号）、date（日期）、asset（资产）、
price（教学用价格）、volume（教学用成交量）。每行是某资产某一天的记录。
A/B 各有四天记录。CSV 表头不计入数据行数，默认索引不计入数据列数。

## 跟练代码

每段放一个单元格，运行前先预测形状。完整注释见 reference.ipynb。

```python
from pathlib import Path
import pandas as pd

data_dir = Path("D:/Learning/study/d9/data")
raw = pd.read_csv(data_dir / "prices.csv", parse_dates=["date"])
df = raw.set_index("record_id")
print(raw.shape)  # (8, 5)
print(df.shape)  # (8, 4)
```

parse_dates 把 date 读成日期类型；避免仅把日期当普通文字理解。

```python
mask_a = df["asset"] == "A"  # 八个逐行判断结果
asset_a = df.loc[mask_a]  # (4, 4)，101、103、105、107
high_price = df.loc[df["price"] > 103]  # (6, 4)
selected = df.loc[(df["asset"] == "A") & (df["price"] > 103)]  # (2, 4)
print(selected)  # 编号 103、107，价格 105、108
```

== 是比较，= 是赋值。& 对两组逐行判断进行并且运算，不能直接换成 and。
每一项比较用括号包起来，确保先完成比较，再组合结果。

```python
shuffled = df.sample(frac=1, random_state=42)
ordered = shuffled.sort_values(by=["asset", "date"], ascending=[True, True])
print(shuffled.index.tolist())
print(ordered.index.tolist())
```

sample 是抽样，frac=1 取全部记录，random_state 固定随机结果便于复现。
sort_values 先按资产排序，再在同一资产内部按日期排序。
排序后索引：[101, 103, 105, 107, 102, 104, 106, 108]，形状仍为 (8, 4)。

```python
print(ordered.iloc[1])  # 位置 1，编号 103，资产 A，价格 105
print(ordered.loc[102])  # 标签 102，资产 B，价格 200
by_id = shuffled.sort_index()  # 按标签排成 101～108
reset_table = ordered.reset_index()  # 编号保留为普通列，形状 (8, 5)
print(reset_table)
```

sort_index 按标签排序，并不普遍等于恢复原始排列；本样本编号恰好与原排列相符。
reset_index(drop=True) 会丢掉旧索引中的编号，因此这里使用不带 drop=True 的版本。

## 独立验收

1. 不看参考代码，独立写出 A、价格 > 103、A 且价格 > 103 三种筛选。
2. 资产 B 且价格 < 200：预计编号 104，形状 (1, 4)。
3. 按价格降序：第一条应是编号 106，价格 205。
4. 打乱后按资产和日期排序，解释结果索引为什么不连续。
5. 对照 loc 与 iloc，解释 reset_index 为什么使数据列数加一。

## 新算法题 217：存在重复元素

https://leetcode.cn/problems/contains-duplicate/description/

用 set（集合）保存此前见过的数字。空集合写 set()，空的 {} 是字典。
遍历每个数字，先查是否见过，见过则返回 True；没见过再 add；
所有数字检查完还没有重复，才返回 False。
集合不表示输入顺序，判断是否出现过不依赖集合的显示顺序。

检查输入：[2, 5, 2] → True；[2, 5, 7] → False；[7] → False；[1, 1] → True。
在 practice.ipynb 从空白实现，再与 cs61A/217.py 对照。
完成后可将独立实现另存为 cs61A/217_practice.py。

## 建议时间

知识点回顾 15 分钟；Pandas 跟练 45～60 分钟；独立练习 30 分钟；
217 集合练习 30～40 分钟；问答及复盘 20 分钟。按薄弱处安排回看视频。

## 官方资料

- https://pandas.pydata.org/pandas-docs/version/2.3/user_guide/indexing.html#boolean-indexing
- https://pandas.pydata.org/pandas-docs/version/2.3/reference/api/pandas.DataFrame.sort_values.html
- https://pandas.pydata.org/pandas-docs/version/2.3/reference/api/pandas.DataFrame.reset_index.html
- https://leetcode.com/problems/contains-duplicate/description/

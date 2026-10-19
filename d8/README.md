# D8：Pandas 读取数据与选择行列

学习目标：从空白代码读入 CSV，观察表格，选择一列、多列、指定行，解释 loc 与 iloc。
本目录数据是虚构的教学样本，不是你的真实学习记录。

## 文件

- data/A.csv：5 条记录，4 列。
- data/B.csv：4 条记录，4 列。
- reference.ipynb：带中文注释的参考 Notebook。
- practice.ipynb：空白练习单元格；完成验收时使用。
- notes.md：今日问答，先独立作答。
- requirements.txt：本次安装的主要软件版本。

## 启动 Notebook

在 PowerShell 输入：

```powershell
& "D:\Learning\Start-Jupyter.cmd"
```

也可以在资源管理器双击这个启动文件。
`&` 是 PowerShell 调用操作符，用于执行引号中的程序或启动文件。
Notebook 会在浏览器中打开，文件列表根目录是 D:\Learning\study。
进入 d8，打开 reference.ipynb，内核选择 Python (D Learning)。
Shift + Enter 运行当前单元格并移到下一格；Ctrl + S 保存。
按顺序运行，前面建立的变量才能供后面使用。
终端持续显示日志是正常的；学习过程中保持终端窗口开启。
结束时在启动终端按 Ctrl + C，如出现确认提示则输入 y 并回车。

## 建议安排

1. 课程视频约 56 分钟；环境已经安装，可以跳过安装演示。
2. 参考 Notebook：40～50 分钟，每次运行前先预测结果形状。
3. 空白 Notebook：30～40 分钟，先独立完成再对照参考。
4. 复做 1480：20～30 分钟，不调用 NumPy。
5. notes.md：15～20 分钟。

## 样本字段

每行是一条学习记录；首行表头不算数据记录。
record_id 是记录编号，day 是第几个学习日，topic 是主题，minutes 单位为分钟。
读取后默认索引为 0、1、2……；record_id 最初仍是普通数据列。

## 从空白开始

在 practice.ipynb 第一格输入：

```python
from pathlib import Path  # Path 表示文件路径
import pandas as pd  # pandas 简写成 pd

data_dir = Path("D:/Learning/study/d8/data")
a = pd.read_csv(data_dir / "A.csv")
b = pd.read_csv(data_dir / "B.csv")

print(a.head(3))  # 前 3 行
print(a.shape)  # (5, 4)，属性不加括号
a.info()  # 查看字段、非空数和数据类型；不要再套 print
```

Notebook 中可在单元格最后单独写变量名显示结果；多项结果使用 print 更明确。
路径采用 / 是 Windows 上 Python 支持的写法，可避免反斜杠转义问题。

## 选择练习与预计形状

| 代码 | 预计结果 |
|---|---|
| a["minutes"] | Series，(5,) |
| a[["minutes"]] | DataFrame，(5, 1) |
| a[["topic", "minutes"]] | DataFrame，(5, 2) |
| a.iloc[1] | 第 2 行，Series，(4,) |
| a.iloc[1:2] | 第 2 行，DataFrame，(1, 4) |
| a.iloc[1:4] | 第 2～4 行，(3, 4) |
| a.iloc[[0, 2], [2, 3]] | 第 1、3 行的 topic、minutes，(2, 2) |

## loc 与 iloc

```python
indexed_a = a.set_index("record_id")  # 新表为 (5, 3)，原表 a 不变
print(indexed_a.loc[102])  # 标签 102，Series，(3,)
print(indexed_a.iloc[1])  # 第 2 个位置，同一条记录
print(indexed_a.loc[102, "minutes"])  # 45

print(indexed_a.loc[101:103, ["topic", "minutes"]])  # (3, 2)
print(indexed_a.iloc[0:3, 1:3])  # (3, 2)，同样的内容
print(indexed_a.iloc[0:2, 1:3])  # (2, 2)，少一行
```

loc 按标签，iloc 按从 0 开始的位置。
在本例已排序、标签唯一的索引上，loc 标签切片包含终点；iloc 位置切片不包含终点。
不能把 iloc 的整数位置当成记录编号，也不能在未设置索引的 a 上用 loc[101] 找记录编号。

## B 表独立验收

1. 读取 B，解释为什么 shape 是 (4, 4)。
2. 选择 topic、minutes，预计 (4, 2)。
3. 选择前两行的这两列，预计 (2, 2)。
4. 用 record_id 设索引后，取 202 号记录的 minutes，预计 40。

## 复做 1480

关闭之前的代码，从空白定义 running_sum(nums)，用循环和列表生成前缀和。
每次累加后追加累计值，循环结束后返回列表。

- [2, 5, -1, 4] → [2, 7, 6, 10]
- [3] → [3]
- [0, 0, 0] → [0, 0, 0]
- [-2, -1, 3] → [-2, -3, 0]

cs61A 中已有 1480.py；复习时可另存 1480_review.py，保留原文件。

## 完成标准

能在空白 Notebook 读取两个 CSV；完成至少 5 次不同选取；
运行前写出形状；解释 Series 与 DataFrame、标签与位置、切片终点；
独立复做 1480 并通过四组检查。

## 官方资料

- https://pandas.pydata.org/pandas-docs/version/2.3/getting_started/intro_tutorials/02_read_write.html
- https://pandas.pydata.org/pandas-docs/version/2.3/getting_started/intro_tutorials/03_subset_data.html
- https://docs.jupyter.org/en/latest/use/jupyter-directories.html

# D15 实操：收益波动与回撤

学习日期：2026-10-29。目标：能解释非年化收益标准差、相对历史峰值的回撤，以及负值/正幅度的区别。
今天只复做第20题，不增加新算法题。先手算，再写代码，全部为教学模拟价格。

## 打开方法与建议节奏

```powershell
# &是PowerShell调用运算符；运行已有的D盘Jupyter启动器。
& "D:\Learning\Start-Jupyter.cmd"
```

若已经启动Jupyter，直接刷新文件列表并进入d15。打开practice.ipynb，右上角内核选Python (D Learning)。
Shift+Enter运行当前格，Ctrl+S保存；重启内核后从第一格顺序运行，不依赖D14或reference里的变量。

1. 课程与knowledge.md 40～60分钟。
2. 四价格手算、A/B风险计算与画图70～90分钟。
3. 有效括号手写栈与复做30～40分钟。
4. 关闭参考，独立复写与回答笔记20～30分钟。

| 文件 | 用途 |
|---|---|
|knowledge.md|知识点、公式、参数和易错点|
|practice.ipynb|留白练习，在里面写自己的代码|
|reference.ipynb|按步骤拆分、每行中文注释的参考|
|data/prices.csv|沿用D14原始模拟CSV，12行3列；不依赖旧输出|
|calculate_risk.py|可直接运行的参考计算与绘图脚本|
|outputs/risk_detail.csv|12行7列，包含收益、净值、峰值、负值回撤|
|outputs/risk_summary.csv|2行6列，包含有效收益数、标准差和两种回撤口径|
|outputs/drawdown_check.csv|100→90→108→81的四行核对表|
|outputs/drawdown.png|A/B负值回撤曲线，百分数坐标|
|20_review.py|第20题复做参考与样例，不改已有cs61A/20.py|
|stack_practice.md|先手写栈，再对照逐步答案|
|notes.md / notes_reference.md|12道问答与分开的答案|

outputs里已有参考验证结果。自己的独立结果请加independent_前缀，便于与参考对照。

## 教学数据与结果核对

| 观测日期 | A价格 | B价格 |
|---|---:|---:|
|2026-10-12|100|200|
|2026-10-13|110|190|
|2026-10-14|99|209|
|2026-10-15|105|205|
|2026-10-16|102|210|
|2026-10-19|108|215|

假设没有分红拆股且价格口径一致，教学观测完整、均为正。缺交易记录时需重新解释收益区间，不能径称日波动。

|资产|价格条数|有效收益数|非年化样本标准差ddof=1|最深回撤负值|最大回撤幅度|
|---|---:|---:|---:|---:|---:|
|A|6|5|约8.1084%|−10%|10%|
|B|6|5|约5.6520%|−5%|5%|

计算和CSV中以小数保存比率，只有展示时格式化为百分数。请先自己计算，再核对这里的答案。


## 1. 先手算四个价格，确认正负号

先在纸上写100→90→108→81。除以第一个价格100，净值依次为1、0.90、1.08、0.81。
历史峰值只查看当前及之前的净值，依次为1、1、1.08、1.08。
回撤=当前净值/截至当期峰值−1，依次为0、−10%、0、−25%。
108创新高时回撤为0，81相对108下降25%。最大回撤负值是−25%，其幅度为正的25%。
末期相对起点100的累计收益是81/100−1=−19%，与最大回撤不是同一个量。

```python
import pandas as pd  # pandas用于表格和序列计算，简称pd

demo = pd.DataFrame({"price": [100, 90, 108, 81]})  # 四个价格构成一列
demo["wealth"] = demo["price"] / demo["price"].iloc[0]  # iloc[0]取首条价格；净值从1开始
demo["peak"] = demo["wealth"].cummax()  # cummax：从开头到当前行的累计最大值
demo["drawdown"] = demo["wealth"] / demo["peak"] - 1  # 回撤采用非正值口径
demo_signed_min = demo["drawdown"].min()  # min取最负的回撤，预计-0.25
demo_mdd = -demo_signed_min  # mdd是maximum drawdown缩写，此处用正的幅度0.25

print(demo)  # 先对照自己手算的四行
print(f"最大回撤负值：{demo_signed_min:.2%}")  # .2%只格式化显示为-25.00%
print(f"最大回撤幅度：{demo_mdd:.2%}")  # 预计25.00%，变量内部仍为0.25
assert abs(demo_mdd - 0.25) < 1e-12  # abs为绝对值；容许极小浮点误差
```


## 2. 从原CSV重新读取并检查

输入是与D14相同的12行3列模拟价格，A/B各六条。仅沿用原始CSV，不使用D14 Notebook的旧变量。
所有转换从raw自己的列读取、写回raw；后续统一使用prices这一张表，不混用line。
假设价格口径一致、无拆股分红且完整为正。日期为教学观测日期，不是真实市场数据。

```python
from pathlib import Path  # Path代表文件路径，/可连接文件夹和文件名

base_dir = Path("D:/Learning/study/d15")  # 今天D15练习所在目录
raw = pd.read_csv(base_dir / "data" / "prices.csv")  # 从原文件读取12行3列
raw["date"] = pd.to_datetime(raw["date"], format="%Y-%m-%d", errors="coerce")  # 非法日期转为NaT
raw["price"] = pd.to_numeric(raw["price"], errors="coerce")  # 非数字价格转为缺失值；coerce须加引号

assert raw[["asset", "date", "price"]].notna().all().all()  # 先逐列再整体检查关键字段非空
duplicate_key = raw.duplicated(subset=["asset", "date"], keep=False)  # subset指定检查重复的两列
assert not duplicate_key.any()  # assert not表示要求“不存在任何重复键”
assert (raw["price"] > 0).all()  # 要求每个价格都大于0，才做本课价格比值
prices = raw.sort_values(["asset", "date"]).reset_index(drop=True)  # 整表先按资产、再按日期升序排列

print(prices)  # 核对A/B各六条，避免资产与价格发生错配
print(prices.shape)  # 此时预计(12, 3)
```


## 3. 收益标准差：仅使用五个有效收益

先在各资产内部计算相邻观测收益；每个资产首条没有上一条价格，因此保持NaN。
std是standard deviation（标准差）的缩写。这里对收益率求标准差，不是对价格求。
ddof是delta degrees of freedom（自由度修正）的缩写；ddof=1使用n−1作方差分母，再开平方。
Pandas的std默认ddof=1且排除缺失值；这里仍显式写出，便于核对。每个资产n=5，不是6。
不要把首条收益fillna(0)，也不乘sqrt(252)。本课结果只称非年化相邻观测收益标准差。

```python
prices["return_pct"] = prices.groupby("asset")["price"].pct_change(fill_method=None)  # 在各资产内计算本期/上期-1
return_count = prices.groupby("asset")["return_pct"].count()  # count只统计非空收益，预计A/B各5个
return_std = prices.groupby("asset")["return_pct"].std(ddof=1)  # 各资产收益的样本标准差，得到带资产索引的Series

print(prices[["asset", "date", "price", "return_pct"]])  # 每个资产首行收益仍应是NaN
print(return_count)  # 预计A=5、B=5
for asset, value in return_std.items():  # items依次取出资产标签和对应标准差
    print(asset, f"非年化收益标准差：{value:.4%}")  # 预计A约8.1084%，B约5.6520%
```


## 4. 每个资产首价归一化为1

transform("first")把本资产首条价格放回本组每一行，因此返回12项，不是两项。
本例关键字段已检查没有缺失，所以first取到的第一项就是首条价格。
wealth是归一化价格净值，含义为当前价格相对本组首价的倍数。
此处从完整价格直接计算；不会用首条未知收益填0，也不会受到旧累计列的影响。

```python
first_price = prices.groupby("asset")["price"].transform("first")  # A组每行为100，B组每行为200，长度仍为12
prices["wealth"] = prices["price"] / first_price  # 每行除以本资产首价，各资产第一行恰好为1

print(prices[["asset", "date", "price", "wealth"]])  # A末期1.08，B末期1.075
```


## 5. 组内历史峰值与回撤

cummax每行给出“截至当前行”的最高净值，包括当前行。创新高或回到峰值时，回撤为0。
必须groupby("asset")后cummax，避免A的历史影响B；也不能用全期max代替，后者会用到未来价格。
drawdown列保留0或负值；不对它整体取绝对值后还把图叫作负值回撤图。
价格比值回撤与净值回撤相同，因为对同一个资产，分子分母都除以相同首价。

```python
prices["peak"] = prices.groupby("asset")["wealth"].cummax()  # 分资产逐行更新截至当期的最高净值
prices["drawdown"] = prices["wealth"] / prices["peak"] - 1  # 当前净值相对此前及当前峰值的下降，结果非正

print(prices[["asset", "date", "wealth", "peak", "drawdown"]])  # 检查峰值不下降、回撤不为正
assert (prices["drawdown"] <= 1e-12).all()  # 容许计算误差；本完整正价样本回撤应不大于0
```


## 6. 汇总风险口径，区分负值与正幅度

每个资产汇成一行，summary为两行。最深回撤取min，不取max；max通常只是0。
标准差Series与汇总表都以asset为索引，所以给新列赋值时按资产标签自动对齐。
return_std不是亏损概率，不能从8.1084%推出“有8.1084%的概率亏损”。
最大回撤只描述本样本已观察到的价格路径，不代表样本开始以前的高点或未观测到的盘中路径。

```python
summary = prices.groupby("asset").agg(  # 每个资产聚合为一行；括号中的名称是自己给结果列起的名字
    price_count=("price", "size"),  # size统计本组记录行数，预计6
    return_count=("return_pct", "count"),  # count统计非空收益数，预计5
    min_drawdown=("drawdown", "min"),  # min取本组最深的负回撤
)  # summary暂以asset为索引
summary["return_std"] = return_std  # 放入前面算好的非年化样本标准差，按资产索引对齐
summary["max_drawdown_magnitude"] = -summary["min_drawdown"]  # 将最负回撤取负号，得到正的最大回撤幅度

print(summary)  # A幅度0.10，B幅度0.05；不要提前把这些小数改成10和5
for asset, row in summary.iterrows():  # iterrows逐行取出资产标签和一行结果，这里仅用于两行展示
    print(asset, f"最大回撤负值：{row['min_drawdown']:.2%}", f"幅度：{row['max_drawdown_magnitude']:.2%}")  # 格式化显示
```


## 7. 画负值回撤曲线，并另存结果

横轴是观测日期，纵轴使用百分数；图标题和纵轴同时写清drawdown<=0（回撤为非正值）。
PercentFormatter(xmax=1)把1显示成100%，所以直接传小数回撤，不再乘100。
Matplotlib的英文标签可以避免当前机器中文字体缺字。图例A/B分别对应两条资产曲线。
导出risk_detail.csv为12行7列，risk_summary.csv为2行6列；CSV内百分率仍存小数。

```python
import matplotlib.pyplot as plt  # pyplot是Matplotlib的绘图接口，简称plt
import matplotlib.dates as mdates  # dates是日期刻度工具，简称mdates
from matplotlib.ticker import PercentFormatter  # 用于把小数坐标显示为百分数

output_dir = base_dir / "outputs"  # output_dir表示输出文件夹路径
output_dir.mkdir(parents=True, exist_ok=True)  # 缺少父文件夹就一起创建；已有时不报错
fig, ax = plt.subplots(figsize=(9, 4.8))  # 创建一张画布fig和一个坐标区域ax，尺寸单位为英寸
for asset, group in prices.groupby("asset"):  # 每轮group是一种资产的六行子表
    ax.plot(group["date"], group["drawdown"], marker="o", label=asset)  # 画该资产的非正值回撤，保留小数
ax.axhline(0, color="gray", linestyle="--", linewidth=1)  # 添加0%参考线
ax.set_title("Drawdown by asset (drawdown <= 0)")  # 标题说明回撤采用非正值
ax.set_xlabel("Observation date")  # 横轴为观测日期
ax.set_ylabel("Drawdown (%, non-positive)")  # 纵轴单位和正负号口径
ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))  # 0.10显示10%，-0.10显示-10%
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))  # 日期标签显示月-日
ax.legend(title="Asset")  # 根据每条plot的label显示资产图例
ax.grid(alpha=0.3)  # 网格用较浅的透明度，便于读数
fig.autofmt_xdate(rotation=30)  # 旋转日期文字，减少重叠
fig.tight_layout()  # 调整布局，避免标题或坐标标签被挤出画布
fig.savefig(output_dir / "drawdown.png", dpi=150, bbox_inches="tight")  # 保存PNG图像
plt.show()  # 在Notebook中显示这张图

prices.to_csv(output_dir / "risk_detail.csv", index=False, encoding="utf-8-sig")  # 保存12行明细，不导出默认索引
summary.reset_index().to_csv(output_dir / "risk_summary.csv", index=False, encoding="utf-8-sig")  # 资产索引转为列后保存
demo.to_csv(output_dir / "drawdown_check.csv", index=False, encoding="utf-8-sig")  # 保存四价格手算核对表
print("已保存：", output_dir)  # 查看CSV与PNG所在文件夹
```


## 8. 栈与有效括号复做

打开stack_practice.md，先手写栈，再独立写函数。右端是栈顶；匹配顺序必须和自己的代码相同。
遇到右括号前先检查空栈；全部读完再判断是否还有左括号。完整逐行参考在20_review.py。

## 从PowerShell运行参考

```powershell
# 用D盘Python运行参考脚本，依据脚本所在目录读取输入并保存图和CSV。
& "D:\py\Python3\python.exe" "D:\Learning\study\d15\calculate_risk.py"

# 运行有效括号复做参考；这里不是向GitHub上传文件的命令。
& "D:\py\Python3\python.exe" "D:\Learning\study\d15\20_review.py"
```

## 独立验收

- 从原CSV重新读取、转换、检查、排序；统一在prices中计算，不借用旧line或旧prices的列。
- A/B各6个价格、5个有效收益；首行NaN未填0；std明确ddof=1且未年化。
- 解释cummax与max区别；输出每行wealth、peak、drawdown。
- 100→90→108→81最大回撤负值为−25%，正幅度为25%，而累计收益为−19%。
- 图的纵轴和标题明确采用负值回撤；A/B的幅度为10%/5%。
- 手写四组栈变化，覆盖错序、缺右括号和开头即右括号，并解释最后的return not stack。
- 完成notes.md，保存自己的practice.ipynb。先完成学习，再提交自己的代码。

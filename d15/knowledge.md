# D15 知识点：收益波动与回撤

学习日期：2026-10-29。本课承接D14；全部使用教学价格，暂不年化，不增加新算法题。

## 1. 先区分三件事

| 名称 | 公式或含义 | 回答什么问题 |
|---|---|---|
| 相邻观测收益 | 本期价格/上一条价格−1 | 相邻两次观测之间涨跌多少 |
| 收益标准差 | 收益相对自身均值的离散程度 | 这段样本的收益上下波动多大 |
| 回撤 | 当前净值/截至当期历史峰值−1 | 相对此前达到过的高点下降多少 |

标准差衡量上下偏离，不能直接当作亏损概率或最大亏损。价格标准差有价格单位，收益标准差是无量纲比率，两者不能混用。

## 2. 非年化样本标准差

设有效收益有n个，平均收益为mean，样本标准差是sqrt(sum((r−mean)^2)/(n−1))。
std是standard deviation的缩写；ddof是自由度修正，ddof=1让分母为n−1。
例如两条收益[0.10,−0.10]，均值0；样本标准差sqrt((0.01+0.01)/1)≈0.141421。
ddof=0时分母是n，结果0.10，两种口径不同。Pandas默认ddof=1，NumPy的np.std默认ddof=0，比较时须显式统一。
只有一个有效收益时，ddof=1的样本标准差是NaN，不是0。

本课A/B各6条价格，所以各有5个相邻观测收益。首行NaN代表缺上一条价格，不填0；std排除缺失后各用5项。
本课不乘sqrt(252)等年化因子。缺少交易记录时，一条相邻观测收益可能跨多个交易日，不能直接把它叫作日收益或日波动。

## 3. 首价归一化、历史峰值、回撤

本例假设无分红拆股、同一价格口径且完整为正：wealth=price/本资产首价，各资产起点为1。
wealth表示净值倍数，wealth−1才是相对起点的累计收益。
peak=wealth.cummax()表示截至当前行、包含当前行的历史最高净值，只使用已有观测。
drawdown=wealth/peak−1，非正。创新高或回到最高点时为0，在峰值下方时为负。
最大回撤负值=drawdown.min()；最大回撤幅度=−drawdown.min()，用正数描述下降幅度。
绘图保留负值；例如−0.25显示−25%，报告幅度则写25%。图里必须说明符号口径。

| 价格 | 归一化净值 | 历史峰值 | 回撤 |
|---:|---:|---:|---:|
|100|1.00|1.00|0%|
|90|0.90|1.00|−10%|
|108|1.08|1.08|0%|
|81|0.81|1.08|−25%|

末期累计收益是81/100−1=−19%；最大回撤幅度是1−81/108=25%。回撤的分母是此前高点，不一定是最初价格。
本课最大回撤仅针对给出的观测区间和价格频率；更早的高点、两次观测之间的价格没有包含在本样本。

## 4. 今天常用命令与接收对象

| 写法 | 对象/参数 | 返回值与用途 |
|---|---|---|
|s.std(ddof=1)|s为收益Series；ddof接整数|一个样本标准差；默认跳过缺失|
|df.groupby("asset")["return_pct"].std(ddof=1)|按资产分组后选收益列|每组一个标准差，结果以asset为索引|
|s.cummax()|按时间排好的数值Series|同长度序列，每行是截至当期的最高值|
|df.groupby("asset")["wealth"].cummax()|每个资产内部计算|12行对应12个峰值，不跨资产|
|s.max()|数值Series|一个全期最大值；不能替代逐行历史峰值|
|s.min()|数值Series|一个最小值；用于负值回撤找最深下降|
|.transform("first")|每组首个非空价格；本课先检查非空|把首价放回该组每一行，行数不变|
|.agg(新列=("原列","统计名"))|结果列名可自定义；元组指定原列和操作|汇总成每资产一行|
|f"{value:.2%}"|value是0.25等小数|显示25.00%；不修改value|
|PercentFormatter(xmax=1)|坐标数据仍使用小数|将1显示成100%，不要再次乘100|

groupby的分组依据是by，可以省略参数名写groupby("asset")；没有subset参数。
subset用于duplicated等方法，用列名或列名列表指定比较范围。coerce是字符串，必须写errors="coerce"。

## 5. 容易写错的地方

- 对price求std：得到价格波动，不能当作本课收益波动。
- 首条收益fillna(0)：人为增加一条零收益，会改变标准差。
- 用wealth.max()算每期峰值：用到了之后的高点；应按时间cummax。
- 忘记groupby：会把两个资产的历史串在一起。
- drawdown.max()当最大回撤：负值曲线的max通常为0，应取min后再转正幅度。
- 全部回撤取abs后仍标负值：图和说明冲突。只对“最大幅度”另列正值。
- 修改上游后只运行绘图格：下游可能仍是旧结果。重启内核后从头运行，统一使用prices。

## 6. 有效括号复习

stack是栈，遵守后进先出。列表右端作为栈顶：append入栈，[-1]只看栈顶，pop取出并删除栈顶。
if not stack表示栈为空，必须先检查再pop，防止空栈IndexError。
右括号必须匹配最近打开且尚未关闭的左括号。读完后return not stack，只有栈为空才成功。
数量相同不代表顺序正确，例如([)]无效。算法时间O(n)、额外空间最坏O(n)。

## 查阅依据

- [Pandas 2.3 GroupBy.std](https://pandas.pydata.org/pandas-docs/version/2.3/reference/api/pandas.core.groupby.DataFrameGroupBy.std.html)
- [Pandas 2.3 Series.std](https://pandas.pydata.org/pandas-docs/version/2.3/reference/api/pandas.Series.std.html)
- [Pandas 2.3 cummax](https://pandas.pydata.org/pandas-docs/version/2.3/reference/api/pandas.Series.cummax.html)
- [CFA Institute：回撤从峰值到随后低点](https://blogs.cfainstitute.org/blog/2013/02/12/sculpting-investment-portfolios-maximum-drawdown-and-optimal-portfolio-strategy/)
- [Python 3.9 中文：列表作为栈](https://docs.python.org/zh-cn/3.9/tutorial/datastructures.html#using-lists-as-stacks)

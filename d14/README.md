# D14 实操：累计收益、滚动均值与绘图

学习日期：2026-10-28。先读knowledge.md，再在practice.ipynb写代码，卡住时看reference.ipynb。
本次全部是模拟数据，延续D13的无拆股分红、价格口径一致假设。

## 打开练习

```powershell
# &调用已有启动器，继续使用D盘Python和Jupyter配置。
& "D:\Learning\Start-Jupyter.cmd"
```

浏览器进入d14，打开practice.ipynb，内核选择Python (D Learning)。
Shift+Enter运行，Ctrl+S保存；内核重启后从第一格重新执行。
若Jupyter已打开，刷新文件列表即可。代码从上往下运行，末节关闭示例独立复写。

建议知识复习45～60分钟，累计收益/均线计算与两张图75～90分钟，栈与第20题40～50分钟，笔记15分钟。

## 文件说明

| 文件 | 用途 |
|---|---|
| knowledge.md | 今日知识点总结与新名称解释 |
| practice.ipynb | 自己的代码与输出，最后一节独立复写 |
| reference.ipynb | 按步骤拆开的逐行中文注释参考 |
| data/prices.csv | 12条完整模拟记录，A/B各六期 |
| outputs/returns_and_ma3.csv | 累计收益与MA3计算表，12行9列 |
| outputs/cumulative_returns.png | A/B累计收益曲线，百分比纵轴 |
| outputs/price_ma3_A.png | A的价格与MA3，两条线及图例 |
| calculate_and_plot.py | 可直接运行、生成CSV与两张图的参考脚本 |
| notes.md | 独立问答题 |
| notes_reference.md | 单独保存的问答参考 |
| D:/Learning/study/cs61A/20.py | 有效括号参考与十一组检查，集中复习 |

输出目录中已有参考验证生成的结果；自己的独立CSV可另存independent_returns_and_ma3.csv。
前六条输入继承D13，再增加10月15、16、19日的A/B记录；不修改D13原样本。

| 日期 | A | B |
|---|---:|---:|
| 2026-10-12 | 100 | 200 |
| 2026-10-13 | 110 | 190 |
| 2026-10-14 | 99 | 209 |
| 2026-10-15 | 105 | 205 |
| 2026-10-16 | 102 | 210 |
| 2026-10-19 | 108 | 215 |

日期都是本次教学观测日期，价格使用样本单位。MA3是三条观测，10月19日窗口包含15、16、19日。


## 1. 手算累计收益：为什么要连乘

起始100，涨10%后变为100×1.1=110，再跌10%后变为110×0.9=99。
两段累计价值倍数是1.1×0.9=0.99，累计收益是0.99-1=-0.01，也就是-1%。
每期都在前一期价值基础上变化，因此连乘的是1+r，而不是直接连乘r或把r简单相加。
本节的两行代表两段已知收益；起始价值1位于第一段之前。


```python
import pandas as pd  # pandas表格处理库，简称pd

demo_returns = pd.Series([0.10, -0.10], name="period_return")  # 两段已知收益，小数形式
demo_factors = 1 + demo_returns  # 每段价值倍数：1.10、0.90
demo_wealth = demo_factors.cumprod(skipna=False)  # cumprod累计连乘，得到1.10、0.99
demo_cumulative = demo_wealth - 1  # 净值倍数减1，得到累计收益0.10、-0.01

print(demo_returns.sum())  # 简单相加为0，不能替代两段累计收益
print(demo_wealth)  # 查看每段结束时的价值倍数
print(demo_cumulative)  # 查看每段结束时的累计收益
print(f"两段累计收益：{demo_cumulative.iloc[-1]:.2%}")  # 预计-1.00%；.iloc[-1]取最后一个结果
```


## 2. 读取并检查六期模拟价格

prices.csv共十二行三列，A/B各六条记录。前三期价格沿用D13，后面增加三期以便观察移动窗口。
日期为2026-10-12、13、14、15、16、19，均为本次教学交易日期；不是真实历史行情。
假设同一价格口径、没有拆股分红，价格完整且为正。先检查，再按资产和日期排序。


```python
from pathlib import Path  # Path用于拼接文件路径

base_dir = Path("D:/Learning/study/d14")  # 本次D14文件夹
raw = pd.read_csv(base_dir / "data" / "prices.csv")  # 读取十二条模拟价格
raw["date"] = pd.to_datetime(raw["date"], format="%Y-%m-%d", errors="coerce")  # 转换日期
raw["price"] = pd.to_numeric(raw["price"], errors="coerce")  # 转换数值价格

print(raw.shape)  # 预计(12,3)
print(raw.isna().sum())  # 本次完整样本各列缺失数都应为0
duplicate_key = raw.duplicated(subset=["asset", "date"], keep=False)  # 仅比较资产和日期是否重复
assert raw[["asset", "date", "price"]].notna().all().all()  # 本份完整样本要求关键字段均非空
assert not duplicate_key.any()  # 要求没有同资产同日期重复记录
assert (raw["price"] > 0).all()  # 本份模拟收盘价均为正数

prices = raw.sort_values(["asset", "date"]).reset_index(drop=True)  # 先排资产，再排日期，并重建默认索引
print(prices)  # A六期100/110/99/105/102/108，B六期200/190/209/205/210/215
```


## 3. 计算每期收益，设置累计指标的起点

先使用D13学过的组内pct_change；return_pct的每个资产首行仍然缺失，不把它填成0。
growth_factor是价值倍数1+r。累计指标以各资产第一条价格为基准，因此只把组首growth_factor设为1。
这表示起始累计净值为1，不代表已经观察到首日真实零收益。

cumcount在每组内按顺序编号，从0开始；所以cumcount()==0标记每个资产的第一行。
后面的中间缺失不能照此填成1，本份完整样本已确认价格没有缺失。


```python
prices["return_pct"] = prices.groupby("asset")["price"].pct_change(fill_method=None)  # 每个资产内部计算收益
prices["growth_factor"] = 1 + prices["return_pct"]  # growth_factor：每期价值倍数
first_in_asset = prices.groupby("asset").cumcount() == 0  # 标记每个资产组内的第一条记录
prices.loc[first_in_asset, "growth_factor"] = 1.0  # 仅初始化累计指标的基准倍数，不修改原始收益列

print(prices[["asset", "date", "price", "return_pct", "growth_factor"]])  # 比较原始首行缺失和基准倍数1
```


## 4. 分资产累计连乘，并用价格比值独立核对

wealth_index表示以首条价格为基准、起始值为1的累计价值倍数；cumulative_return为它减1。
cumprod也必须在每个资产内部计算。skipna=False表示中间若出现缺失，不跳过去继续形成累计路径。
本例价格完整，所以会得到完整结果；在真实缺失数据上要先解释收益区间。

用另一条恒等关系核对：本期价格/本资产第一条价格-1。
transform("first")把本组第一条价格对应回组内每一行，本完整样本的首价非空。
浮点计算可能有微小差异，用绝对误差阈值核对，不要求严格等于字面量0.1。


```python
prices["wealth_index"] = prices.groupby("asset")["growth_factor"].cumprod(  # 各资产内部累计连乘价值倍数
    skipna=False,  # 如果中间缺失，从缺口起保留未知，不自动跨过
)  # 每个资产首行从1开始
prices["cumulative_return"] = prices["wealth_index"] - 1  # 起始累计收益为0，此后表示相对首价的变化

first_price = prices.groupby("asset")["price"].transform("first")  # 给每一行对应本资产的首条价格
prices["return_from_price"] = prices["price"] / first_price - 1  # 用首尾价格比直接核对
maximum_error = (prices["cumulative_return"] - prices["return_from_price"]).abs().max()  # 计算最大绝对误差
print("两种累计计算的最大差异：", maximum_error)  # 预计为0或极小浮点误差
assert maximum_error < 1e-10  # 1e-10表示10的负10次方，用作本例核对容差

print(prices[["asset", "date", "wealth_index", "cumulative_return", "return_from_price"]])  # A第三期为-1%，末期8%；B末期7.5%
```


## 5. 用三期小例子理解滚动均值

rolling(window=3)默认从当前行向前取最近三条观测，包含当前行。
min_periods=3要求窗口内至少三个非空价格；不足时结果为NaN。
对100/110/99，前两条不足三个值，第三条均价=(100+110+99)/3=103。
加入第四条105后，窗口移动成110/99/105，均价为104.6667。
这里“三期”是三条观测，不是三个自然日。10月19日的窗口可包含10月15、16、19日。


```python
demo_prices = pd.Series([100, 110, 99, 105], name="price")  # 用四条价格观察窗口如何移动
demo_ma3 = demo_prices.rolling(  # rolling创建滚动窗口
    window=3,  # 每个窗口取最近三条观测
    min_periods=3,  # 至少三个非空价格才输出结果
).mean()  # 对每个窗口求算术平均数

print(demo_ma3)  # 预计NaN、NaN、103、104.6667
```


## 6. 在各资产内部计算MA3

MA是moving average（移动平均）的缩写，ma3是我们给三期均价列起的名字。
transform把每组计算结果放回对应的原始行，仍然是十二行，不像agg变成两行。
lambda中的s是当前资产整组价格Series，不是单个数字。
先在组内按最近三条观测建立窗口，窗口中有三个非空价格才输出均值。
本完整样本每组前两条均价缺失，共四个缺失；不要填0，否则图上会出现不存在的零价均线。


```python
prices["ma3"] = prices.groupby("asset")["price"].transform(  # 分资产计算，并保持与原行对齐
    lambda s: s.rolling(window=3, min_periods=3).mean()  # s是一组价格；滚动三条后求每个窗口的均值
)  # 返回的每一条均价放到对应的资产和日期行

print(prices[["asset", "date", "price", "ma3"]])  # 检查每个资产前两行都为NaN
print("均价缺失总数：", int(prices["ma3"].isna().sum()))  # 预计4，A/B各2条
```


## 7. 绘制A/B累计收益曲线

一张图中每条线代表一项资产，纵轴按百分数显示，所以绘图时把小数收益乘100。
计算表中的cumulative_return仍保留小数，不改为带百分号的文字。
label为每条线命名，legend显示图例；日期横轴包含本次六个观测日期。
图中文字用英文，避免本机中文字体配置影响显示，解释和代码注释继续使用中文。


```python
import matplotlib.pyplot as plt  # pyplot绘图接口，简称plt
import matplotlib.dates as mdates  # 日期坐标格式工具，简称mdates

output_dir = base_dir / "outputs"  # 设置图表和CSV的输出文件夹
output_dir.mkdir(parents=True, exist_ok=True)  # 必要时创建目录，已经存在则继续
plot_dates = prices["date"].drop_duplicates().sort_values()  # 本次六个不同的观测日期

fig, ax = plt.subplots(figsize=(8, 4.8))  # fig是整张图，ax是坐标区域；尺寸单位为英寸
for asset, group in prices.groupby("asset"):  # 每轮取一项资产代码和该资产的整张子表
    ax.plot(  # 将这一项资产画成一条折线
        group["date"],  # 横坐标：该资产的日期
        group["cumulative_return"] * 100,  # 纵坐标：只在绘图时转换为百分数数值
        marker="o",  # 用圆点标记每个观测日期
        label=f"Asset {asset}",  # 图例名称，例如Asset A
    )  # 当前资产曲线添加完成

ax.set_title("Cumulative returns from first price")  # 标题说明以首条价格为基准
ax.set_xlabel("Date")  # 横轴名称
ax.set_ylabel("Cumulative return (%)")  # 纵轴名称和百分比单位
ax.set_xticks(plot_dates)  # 明确显示六个观测日期刻度
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))  # 日期刻度简写为月-日
ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)  # 画零累计收益参考线
ax.grid(alpha=0.3)  # 淡色网格，alpha控制透明度
ax.legend()  # 显示每条曲线label对应的图例
fig.autofmt_xdate(rotation=30)  # 旋转日期文字，减少重叠
fig.tight_layout()  # 调整布局，避免标题与轴标签被裁切
fig.savefig(output_dir / "cumulative_returns.png", dpi=150, bbox_inches="tight")  # 保存PNG图片
plt.show()  # 在Notebook中显示图像
```


## 8. 绘制A的价格与三期均线

这张图只画A，用两条线分别显示原始价格和MA3，方便观察均线从第三期开始出现。
均价前两项保留NaN，Matplotlib不会把它们画成0。
价格和均价单位相同，纵轴写Price (sample units)，因为本次没有指定货币单位。


```python
a_prices = prices.loc[prices["asset"] == "A"].copy()  # 取出A的六条价格与计算结果
fig, ax = plt.subplots(figsize=(8, 4.8))  # 创建新的独立图像和坐标区域
ax.plot(a_prices["date"], a_prices["price"], marker="o", label="Price")  # 绘制A价格曲线
ax.plot(a_prices["date"], a_prices["ma3"], marker="s", linestyle="--", label="MA3")  # 绘制A三期均线
ax.set_title("Asset A price and 3-observation mean")  # 标题，强调三条观测均值
ax.set_xlabel("Date")  # 横轴为日期
ax.set_ylabel("Price (sample units)")  # 纵轴为样本价格单位
ax.set_xticks(plot_dates)  # 显示本次六个观测日期
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))  # 日期显示为月-日
ax.grid(alpha=0.3)  # 添加淡色网格
ax.legend()  # 显示Price与MA3图例
fig.autofmt_xdate(rotation=30)  # 旋转日期标签
fig.tight_layout()  # 调整边距，避免文字裁切
fig.savefig(output_dir / "price_ma3_A.png", dpi=150, bbox_inches="tight")  # 保存价格均线图
plt.show()  # 在Notebook中显示图像
```


## 9. 保存计算表并核对末期结果

计算表保留十二条记录和九列，不把原始收益首行缺失或均线开头缺失填掉。
最后一期累计收益：A=8%，B=7.5%；A第三期累计收益=-1%。
CSV保存小数收益，日期格式明确；打开表时，空字段代表缺失，不代表0。


```python
prices.to_csv(  # 保存完整计算表
    output_dir / "returns_and_ma3.csv",  # 十二行九列的参考结果
    index=False,  # 不另存默认数字索引
    encoding="utf-8-sig",  # 使用方便Windows识别的编码
    date_format="%Y-%m-%d",  # 日期输出为年-月-日
)  # CSV保存完成
print(prices.groupby("asset").tail(1)[["asset", "date", "cumulative_return", "ma3"]])  # 查看各资产末条结果
print(prices.shape)  # 预计(12,9)
print("结果文件夹：", output_dir)  # 显示CSV和两张图的保存位置
```


## 10. 用列表体验栈的后进先出

先读Python中文教程的“用列表实现堆栈”。栈是后进先出，英文缩写LIFO：Last In, First Out。
本题用列表末尾作为栈顶。append加入末尾；pop取出并删除末尾；[-1]只查看末尾，不删除。
[]创建列表，{}创建空字典。先判断是否为空，再从栈中取值。


```python
stack_demo = []  # 用空列表表示空栈
stack_demo.append("(")  # 先放入左圆括号
stack_demo.append("[")  # 再放入左方括号，栈顶变成[
print(stack_demo)  # 预计['(', '[']
print(stack_demo[-1])  # 只查看最后一个元素，预计[
opening = stack_demo.pop()  # 取出并删除最后放入的元素，预计[
print("取出的括号：", opening)  # 查看pop的返回值
print("剩下的栈：", stack_demo)  # 预计只剩['(']
```


## 11. 有效的括号：实现并检查

原题字符串只含()[]{}。左括号加入栈；遇到右括号，必须匹配最近尚未闭合的左括号。
遇到右括号时栈为空，或栈顶类型不对应，立即返回False。
遍历全部字符后，栈仍有左括号也无效，因此最后返回not stack。
not空列表为True，not非空列表为False。这一句在循环外，不能第一对匹配后就返回True。
"([)]"虽然每种左右括号数量相等，但关闭顺序错误，必须返回False。
原题不含空串，本地额外用空串检查函数边界，约定返回True。


```python
def is_valid(s):  # 接收只含()[]{}的字符串，返回括号是否正确配对
    stack = []  # stack是栈，用列表保存尚未匹配的左括号
    pairs = {  # 字典：每种右括号对应它需要的左括号
        ")": "(",  # 右圆括号需要左圆括号
        "]": "[",  # 右方括号需要左方括号
        "}": "{",  # 右花括号需要左花括号
    }  # 对应关系创建完成

    for char in s:  # char是character的缩写，每次读取一个括号字符
        if char in "([{":  # 当前字符是三种左括号之一
            stack.append(char)  # 将左括号加入列表末尾，也就是入栈
        else:  # 原题限定字符集，因此其余字符一定是右括号
            if not stack:  # 空列表为False，not stack表示栈为空
                return False  # 没有等待匹配的左括号，立即判定无效

            opening = stack.pop()  # 取出并删除最后加入的左括号，体现后进先出
            if opening != pairs[char]:  # 取出的左括号必须与当前右括号类型相同
                return False  # 类型不匹配，立即判定无效

    return not stack  # 全部读完后，只有栈为空才有效；这句在for循环外

examples = [  # 每项保存：输入字符串和预期布尔结果
    ("()", True),  # 一对括号
    ("()[]{}", True),  # 多对括号并列
    ("([])", True),  # 正确嵌套
    ("{[()]}", True),  # 三层正确嵌套
    ("([)]", False),  # 数量相等，但关闭顺序错误
    ("(]", False),  # 左右类型不匹配
    ("(", False),  # 还剩未闭合的左括号
    (")", False),  # 没有左括号就遇到右括号
    ("(((", False),  # 多个左括号未闭合
    ("{[]}", True),  # 正确嵌套的花括号与方括号
    ("", True),  # 本地扩展：空串没有未匹配括号；原题长度至少为1
]  # 样例定义完毕

for text, expected in examples:  # 每轮取出一组输入与预期结果
    actual = is_valid(text)  # 调用自己写的括号检查函数
    print(repr(text), "->", actual)  # repr让空串也能清楚显示为引号
    assert actual is expected  # 检查实际布尔结果与预期一致

print("有效括号十一组检查通过。")  # 全部样例通过才输出这句话
```


## 12. 独立验收

- 关闭参考，重新读取原CSV，独立计算收益、首价累计基准、组内累计连乘、MA3和两张图。
- 保留return_pct组首NaN，保留ma3组首两条NaN。
- 用首价比值核对累计结果，解释A第三期为何为-1%，A末期8%、B末期7.5%。
- 图有标题、坐标说明和图例；累计收益图单位为%，价格图单位为样本价格。
- 手动追踪"([])"和"([)]"，独立写出is_valid，末尾检查栈是否为空。
- 保存自己的practice.ipynb，回答notes.md，再对照notes_reference.md。

## 运行参考脚本

```powershell
# 计算和绘图脚本依据自身位置找数据，保存后关闭图像，不等待窗口。
& "D:\py\Python3\python.exe" "D:\Learning\study\d14\calculate_and_plot.py"

# 有效括号参考与样例检查。
& "D:\py\Python3\python.exe" "D:\Learning\study\cs61A\20.py"
```

## 常见问题

累计结果全缺失：是否在保留首行NaN的价值倍数上直接用了skipna=False？本课只初始化每组首个growth_factor为1，原return_pct不改。

累计收益出现跨资产混算：cumprod也要groupby，不能只在pct_change时分组。

均线从第一条就出现：检查min_periods是否误设为1。本课要求完整三期均值。

均线出现0：不要fillna(0)，窗口不足表示未知，0不是已计算的均价。

图例没有曲线名称：每条plot写label，再调用legend。

累计图显示0.08但轴标%：绘图时乘100；计算表中的0.08仍然表示8%。

pop报IndexError：先用if not stack判断空栈，再取出栈顶。

"([)]"被判断有效：不能只计数左右括号，应按栈顶检查最近打开的括号。

## 查阅

- [Pandas 2.3 cumprod](https://pandas.pydata.org/pandas-docs/version/2.3/reference/api/pandas.Series.cumprod.html)
- [Pandas 2.3 rolling](https://pandas.pydata.org/pandas-docs/version/2.3/reference/api/pandas.DataFrame.rolling.html)
- [Python中文栈教程](https://docs.python.org/zh-cn/3/tutorial/datastructures.html#using-lists-as-stacks)
- [20：有效的括号](https://leetcode.cn/problems/valid-parentheses/description/)

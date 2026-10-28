# D13 实操：简单收益率、滞后与日期核对

学习日期：2026-10-26。本次全部为模拟教学数据，不是真实历史行情。
用户已选择先使用教学样本；以后拿到真实历史CSV，再检查价格口径并复用核心流程。

## 先打开什么

1. 阅读knowledge.md，先把100→110→99写在纸上，算出每段收益。
2. 打开practice.ipynb写自己的代码；卡住时对照reference.ipynb相同编号的步骤。
3. 最后关闭示例，独立复写，回答notes.md，再对照notes_reference.md。

```powershell
# &执行已有启动器，继续使用D盘Python、Jupyter和配置。
& "D:\Learning\Start-Jupyter.cmd"
```

浏览器进入d13；内核选Python (D Learning)。Shift+Enter运行，Ctrl+S保存。
Jupyter已打开时刷新文件列表即可，重启内核后从前往后重新运行。

建议视频/知识复习45～60分钟，手算与核心流程60分钟，缺失实验40～50分钟，独立复写与笔记30分钟。
今天不增加新算法题。第10节补日期为选做，其余围绕收益与日期核对。

## 文件说明

| 文件 | 用途 |
|---|---|
| knowledge.md | 今日知识点，含价格口径和小数/百分比解释 |
| practice.ipynb | 自己的代码与输出，末节从空白独立复写 |
| reference.ipynb | 每步附中文注释的完整参考 |
| data/prices.csv | 六条乱序的完整模拟记录 |
| data/prices_missing_value.csv | 六条记录仍在，仅A的10月13日价格缺失 |
| data/prices_missing_row.csv | 删除A的10月13日整条记录，仅剩五条 |
| data/trading_calendar.csv | 仅三天的教学交易日序号，不是正式交易所日历 |
| outputs/returns.csv | 完整样本收益，六行七列 |
| outputs/missing_value_returns.csv | 缺价格对照，六行五列 |
| outputs/missing_row_audit.csv | 缺整行的日期区间核对，五行九列 |
| calculate_returns.py | 可直接运行的完整参考脚本 |
| notes.md | 独立问答题 |
| notes_reference.md | 单独存放的问答参考答案 |

outputs中已有参考流程验证生成的结果。独立练习另存independent_returns.csv，由你自己运行后生成。
CSV中保留小数收益，缺失保存为空字段；空字段不是0。

## 今天的价格假设

A/B是虚构资产，price是统一口径的模拟收盘价格，无拆股、分红等公司行动，价格单位一致。
字段名price本身不能证明真实数据是否复权；真实数据需查看供应商定义。

| 教学日期 | A价格 | B价格 |
|---|---:|---:|
| 2026-10-12 | 100 | 200 |
| 2026-10-13 | 110 | 190 |
| 2026-10-14 | 99 | 209 |

主文件故意乱序，因此必须先排序。以下代码在同一Notebook中从上到下执行。


## 1. 先在纸上手算 100 → 110 → 99

写出每个分母：110/100-1=0.10，也就是+10%；99/110-1=-0.10，也就是-10%。
第二次的分母是110，不是最初的100。全区间99/100-1=-0.01，即-1%。
因此涨10%后跌10%并不回到原点。
本节只做数值手算，不需要新增算法题。


```python
up_return = 110 / 100 - 1  # 第一段简单收益率：本期价格除以上期价格，再减一
down_return = 99 / 110 - 1  # 第二段的上期价格是110，所以分母改为110
whole_return = 99 / 100 - 1  # 从最初100到最终99的整个区间收益率

print("第一段：", up_return)  # 约0.10，浮点数可能显示少量尾数
print("第二段：", down_return)  # 约-0.10
print("整个区间：", whole_return)  # 约-0.01
print(f"第一段：{up_return:.2%}")  # f字符串中的.2%：按百分比显示，并保留两位小数
print(f"第二段：{down_return:.2%}")  # 显示-10.00%，不改变变量里保存的小数
print(f"整个区间：{whole_return:.2%}")  # 显示-1.00%
```


## 2. 用 shift 与 pct_change 对照手算

shift(1)在这里不设置freq，表示把前一条观测的价格放到当前行。
对[100,110,99]，前值是[缺失,100,110]，当前价格除以前值再减一即可。
pct_change(fill_method=None)直接计算相邻观测的变化率，不自动填价格缺失值。
pct是percentage的常用缩写，但该方法返回小数变化率：0.1表示10%，不是0.1%。
第一行没有前值，所以无法计算，保留NaN，不填成0。


```python
import pandas as pd  # pandas表格处理库，通常简称pd

demo = pd.DataFrame({"price": [100, 110, 99]})  # 建立三行一列的小样本
demo["prev_price"] = demo["price"].shift(1)  # prev是previous的缩写，表示前一条价格
demo["return_formula"] = demo["price"] / demo["prev_price"] - 1  # 直接按公式计算
demo["return_pct"] = demo["price"].pct_change(  # 用Pandas方法计算同样的变化率
    fill_method=None,  # None：不要在计算前自动填充缺失价格
)  # 预计为NaN、0.10、-0.10；返回值仍是小数

print(demo)  # 对照价格、前值、两种计算结果
print(demo.shape)  # 预计(3,4)，增加了前值和两列收益率
```


## 3. 读取乱序的多资产教学数据，检查后排序

用户已选择教学样本。本次所有价格均为模拟收盘价格，假设没有拆股、分红等公司行动，口径统一。
prices.csv有六行三列，故意打乱：A在三天的价格是100/110/99，B是200/190/209。
日期为2026-10-12、13、14。它们在本教学日历里是三个连续交易日，不代表正式交易所日历。

先检查列类型、缺失、同资产同日重复、非正价格，再按asset和date升序排列。
assert用于核对本份完整样本的预期前提；不满足时停止，先检查数据，不继续算。
本节主样本价格都不缺失；后面的缺失实验会使用另外两个文件。


```python
from pathlib import Path  # Path：表示和拼接文件路径

base_dir = Path("D:/Learning/study/d13")  # 本次D13文件夹的绝对路径
raw = pd.read_csv(base_dir / "data" / "prices.csv")  # 读取六条乱序的模拟价格
raw["date"] = pd.to_datetime(raw["date"], format="%Y-%m-%d", errors="coerce")  # 转换日期
raw["price"] = pd.to_numeric(raw["price"], errors="coerce")  # 转换价格，失败变缺失

print(raw)  # 先观察原来的乱序
raw.info()  # 查看列类型和非空数
print(raw.isna().sum())  # 完整样本三列缺失数都应为0
duplicate_key = raw.duplicated(subset=["asset", "date"], keep=False)  # 标记同资产同日重复
print("重复键行数：", int(duplicate_key.sum()))  # 预计0
print("非正价格行数：", int((raw["price"] <= 0).sum()))  # 预计0，零不能作为收益公式分母

assert raw[["asset", "date", "price"]].notna().all().all()  # 确认这份完整样本关键字段均非空
assert not duplicate_key.any()  # 一项资产一天只能有一条价格，避免前值含义不明确
assert (raw["price"] > 0).all()  # 本份收盘价样本要求价格为正

prices = raw.sort_values(["asset", "date"]).reset_index(drop=True)  # 先排资产，再排日期，并重建行索引
print(prices)  # 预计先是A的三天，再是B的三天
print(prices.shape)  # 排序不删除记录，仍为(6,3)
```


## 4. 在每个资产内部取得前一条价格和日期

先groupby资产，再shift，保证A只与A比较，B只与B比较。
同时保留prev_date，让你能直接看到本次收益到底覆盖哪两个日期。
shift(1)指组内前一条观测，默认不搜索上一个交易日，也不会补出缺失交易记录。
完整样本中每个资产首行的prev_price为NaN，prev_date为NaT；这代表当前输入区间没有前值。


```python
prices["prev_price"] = prices.groupby("asset")["price"].shift(1)  # 每个资产内部的前一条价格
prices["prev_date"] = prices.groupby("asset")["date"].shift(1)  # 每个资产内部的前一条记录日期
prices["return_formula"] = prices["price"] / prices["prev_price"] - 1  # 按本期/上期-1计算

print(prices[["asset", "date", "price", "prev_date", "prev_price", "return_formula"]])  # 逐行核对分母和日期
print("没有前值的行：")  # 下方在本完整样本中应是A、B各一条首行
print(prices.loc[prices["prev_price"].isna(), ["asset", "date"]])  # 用布尔筛选查看组首
```


## 5. 使用分组 pct_change，并与公式核对

groupby("asset")["price"]先创建按资产分组的价格序列，再分别计算pct_change。
不要对包含所有资产的price整列直接计算，否则在资产边界会串组。
equals返回单个布尔值；本例两种算法结果相同，并把同位置的NaN视为相同。
用round只是显示时看清楚，不需要提前把计算中的收益率四舍五入。


```python
prices["return_pct"] = prices.groupby("asset")["price"].pct_change(  # 在各资产内部计算相邻观测收益
    fill_method=None,  # 不自动填充缺失价格
)  # 返回的小数与按公式得到的收益率对应

print(prices[["asset", "date", "price", "prev_price", "return_formula", "return_pct"]])  # 比较两种方法
print("两种结果是否一致：", prices["return_formula"].equals(prices["return_pct"]))  # 本例预计True
print("仅按百分数数值显示：", (prices["return_pct"] * 100).round(2))  # 10表示10%，底层收益列仍保存0.1
```


## 6. 错误对照：为什么不能全表直接计算

本节故意演示错误，不用于导出或独立练习答案。
已经排好顺序时，A最后一行价格99，B第一行价格200；全表计算会把B的200除以A的99。
B的首行应缺失，而错误对照会显示约102.02%的变化。这是在跨资产比较。
日期排序只解决顺序，groupby才明确每条收益属于哪个资产。


```python
wrong_global = prices[["asset", "date", "price"]].copy()  # 创建错误演示专用副本，不修改正确结果
wrong_global["wrong_return"] = wrong_global["price"].pct_change(fill_method=None)  # 故意漏掉groupby
print(wrong_global.loc[wrong_global["asset"] == "B"].head(1))  # B首行得到错误的跨资产变化率
```


## 7. 记录存在，但中间价格缺失

prices_missing_value.csv仍有六行，A的10月13日记录存在，但price留空。
A的价格是[100,缺失,99]。fill_method=None下：
第一行没有前值；第二行当前价格缺失；第三行前一条价格缺失，因此A三条收益都缺失。
它不会自动跳过空价格，拿更早的100当第三行的分母。
如果先dropna删掉空价格行，就改变了比较区间，结果将类似下一节缺整行实验。


```python
missing_value = pd.read_csv(base_dir / "data" / "prices_missing_value.csv")  # 读取记录存在但价格为空的样本
missing_value["date"] = pd.to_datetime(missing_value["date"], format="%Y-%m-%d")  # 转换日期
missing_value["price"] = pd.to_numeric(missing_value["price"], errors="coerce")  # 空价格保持缺失
missing_value = missing_value.sort_values(["asset", "date"]).reset_index(drop=True)  # 排好组内时间顺序
missing_value["prev_price"] = missing_value.groupby("asset")["price"].shift(1)  # 前一条为空就保留为空
missing_value["return_pct"] = missing_value.groupby("asset")["price"].pct_change(fill_method=None)  # 不填补价格

print(missing_value.loc[missing_value["asset"] == "A"])  # A三条return_pct都为NaN
print(missing_value.shape)  # 仍有六行，新增两列后为(6,5)
```


## 8. 整条交易记录缺失：观察收益的实际日期区间

prices_missing_row.csv删除了A的10月13日整条记录，总共五行。
A只剩10月12日100与10月14日99，pct_change会计算99/100-1=-1%。
公式没有错，但结果跨了教学日历中的两个交易区间，不能直接称为一交易日收益。
fill_method=None只控制价格缺失值的填充，不能发现文件里根本不存在的日期行。


```python
missing_row = pd.read_csv(base_dir / "data" / "prices_missing_row.csv")  # 读取缺少A中间整条记录的样本
missing_row["date"] = pd.to_datetime(missing_row["date"], format="%Y-%m-%d")  # 转换日期
missing_row["price"] = pd.to_numeric(missing_row["price"], errors="coerce")  # 转换价格
missing_row = missing_row.sort_values(["asset", "date"]).reset_index(drop=True)  # 按资产和日期排序
missing_row["prev_price"] = missing_row.groupby("asset")["price"].shift(1)  # A的99对应的前价变成100
missing_row["prev_date"] = missing_row.groupby("asset")["date"].shift(1)  # A的10月14日前一观测日为10月12日
missing_row["return_pct"] = missing_row.groupby("asset")["price"].pct_change(fill_method=None)  # 计算相邻观测收益

print(missing_row.loc[missing_row["asset"] == "A"])  # 重点观察prev_date、prev_price及-0.01
print("输入记录数：", len(missing_row))  # 预计5，缺的是一整行
```


## 9. 用教学交易日序号标记跨交易区间

trading_calendar.csv只有三个教学交易日，session_no依次为1、2、3。
session表示交易时段；本例一天一个时段。session_gap是当前序号减去前一观测序号。
A从10月12日到14日的序号差为2，说明跨两个交易区间。
不用自然日差大于1来判断缺交易记录：周末或休市也会有自然日间隔。
真实数据要换成对应市场、资产的交易日历，并核实缺失是漏数、停牌还是其他原因。

where(条件)在条件为True时保留原值，为False时变成缺失。
return_one_session只保留session_gap==1的收益，本例A的跨区间-1%会被保留在原收益列、在这一列置缺失。
组首没有前值，session_gap本身也缺失，不能解释成0个交易区间收益。


```python
calendar = pd.read_csv(base_dir / "data" / "trading_calendar.csv")  # 读取三天教学日历
calendar["date"] = pd.to_datetime(calendar["date"], format="%Y-%m-%d")  # 转换日历日期
gap_audit = pd.merge(  # 给缺行样本补充每个日期对应的交易日序号
    missing_row,  # 左表：五条实际观测记录
    calendar,  # 右表：日期对应session_no
    on="date",  # 根据日期匹配
    how="left",  # 保留实际观测记录，不自动补出缺失行
    validate="many_to_one",  # 日历中的每个日期必须唯一
)  # 合并后仍然五行
gap_audit = gap_audit.sort_values(["asset", "date"]).reset_index(drop=True)  # 明确组内观测顺序
assert gap_audit["session_no"].notna().all()  # 本例每条观测日期都必须能在教学日历中找到
previous_session = gap_audit.groupby("asset")["session_no"].shift(1)  # 同一资产前一观测的交易日序号
gap_audit["session_gap"] = gap_audit["session_no"] - previous_session  # 计算相邻观测跨几个交易区间
gap_audit["return_one_session"] = gap_audit["return_pct"].where(  # 单独保留只跨一个交易区间的收益
    gap_audit["session_gap"] == 1,  # 只有序号差为1才保留；其余置为缺失
)  # 原始相邻观测收益return_pct保持不变，便于核对

print(gap_audit[["asset", "prev_date", "date", "return_pct", "session_gap", "return_one_session"]])  # 查看收益区间
```


## 10. 选做：补齐日期不等于补出真实价格

这一步只演示A，不涉及跨资产。日历作为左表，把缺失的10月13日日期补出来。
那天的真实价格仍然未知，price是NaN；不填价格时，相邻交易日收益也不能计算。
补行只是显露缺口，不是恢复了历史行情。主线掌握后再做本节即可。


```python
a_observed = missing_row.loc[missing_row["asset"] == "A", ["date", "price"]].copy()  # 只取A的两条实际观测
a_calendar = pd.merge(  # 以教学日历为左表补出日期
    calendar[["date"]],  # 三个完整的教学交易日
    a_observed,  # A只有两个日期有价格
    on="date",  # 根据日期匹配
    how="left",  # 保留日历中的三天
    validate="one_to_one",  # 两边每个日期都必须唯一
)  # 缺少的10月13日出现，但价格仍然缺失
a_calendar["return_pct"] = a_calendar["price"].pct_change(fill_method=None)  # 只含A，直接对该价格序列计算
print(a_calendar)  # 三条收益都无法计算，不能用补日期替代找回价格
```


## 11. 保存正确结果，独立复写核心流程

保存三份参考结果：完整样本收益、缺价格实验、缺行区间核对。
CSV中的收益率继续保存小数，不把0.1写成文本10%。首行空字段表示缺失，不表示零收益。
date_format控制日期输出，CSV不保留Pandas类型信息。

完成后关闭参考，在practice.ipynb最后一节重新读取prices.csv，独立完成检查、排序、分组前值、两种收益计算和保存。
自己的结果另存为outputs/independent_returns.csv，避免混淆参考结果与独立练习。


```python
output_dir = base_dir / "outputs"  # 设置结果文件夹
output_dir.mkdir(parents=True, exist_ok=True)  # 上级目录可一并创建，已存在则继续

prices.to_csv(  # 保存完整样本的正确收益计算，不保存错误对照
    output_dir / "returns.csv",  # 六行七列，包含前值和两种收益率
    index=False,  # 不另存默认数字行索引
    encoding="utf-8-sig",  # 使用方便Windows识别的编码
    date_format="%Y-%m-%d",  # 日期和前一日期均按年-月-日输出
)  # 完整样本结果保存完毕
missing_value.to_csv(  # 保存六行的缺价格对照
    output_dir / "missing_value_returns.csv",  # A三条收益都缺失，B不受影响
    index=False,  # 不输出额外索引
    encoding="utf-8-sig",  # 使用带标记的UTF-8编码
    date_format="%Y-%m-%d",  # 日期按年-月-日输出
)  # 缺价格对照保存完毕
gap_audit.to_csv(  # 保存五行的缺整行区间核对
    output_dir / "missing_row_audit.csv",  # 同时保存跨观测收益和只跨一交易区间的收益
    index=False,  # 不输出额外索引
    encoding="utf-8-sig",  # 使用带标记的UTF-8编码
    date_format="%Y-%m-%d",  # 日期列使用一致格式
)  # 区间核对表保存完毕

print("完整样本结果形状：", prices.shape)  # 预计(6,7)
print("缺价格结果形状：", missing_value.shape)  # 预计(6,5)
print("缺整行核对形状：", gap_audit.shape)  # 预计(5,9)
print("结果文件夹：", output_dir)  # 显示保存位置
```


## 完整样本的预期结果

| asset | date | price | prev_price | return_pct |
|---|---|---:|---:|---:|
| A | 2026-10-12 | 100 | 缺失 | 缺失 |
| A | 2026-10-13 | 110 | 100 | 0.10 |
| A | 2026-10-14 | 99 | 110 | -0.10 |
| B | 2026-10-12 | 200 | 缺失 | 缺失 |
| B | 2026-10-13 | 190 | 200 | -0.05 |
| B | 2026-10-14 | 209 | 190 | 0.10 |

## 今天的完成标准

- 能独立写出本期价格/上期价格-1，手算+10%、-10%和整个区间-1%。
- 能先按asset/date排序，再在各资产内部shift与pct_change(fill_method=None)。
- 能逐行指出prev_date和date，解释每个资产首行为什么缺失，为什么不能填0。
- 能解释缺行时算出的-1%覆盖两个交易区间，不自动称为日收益。
- 能区分缺整行与价格单元格缺失，并说明fill_method=None不负责发现缺行。
- 保存自己的Notebook和独立结果，回答notes.md。

## 直接运行参考脚本

```powershell
# &调用D盘Python，脚本按自身位置找数据，当前终端可在D:/Learning。
& "D:\py\Python3\python.exe" "D:\Learning\study\d13\calculate_returns.py"
```

脚本会更新三份参考CSV，不会自动填写你的practice.ipynb。

## 常见问题

收益显示0.10000000000000009：浮点近似，显示时用百分比格式；验证可用容差，不要求严格等于字面量0.1。

第一行为什么不是0：没有前一价格，所以未知；0代表确实没有价格变化，两者不同。

B首行出现很大收益：检查是否漏了groupby，错拿A的最后一价当分母。

fill_method=None后仍出现跨日期收益：检查是不是缺了一整行。None不填价格缺失，不会自动补齐日期。

不知道有没有缺交易记录：需对照对应市场/资产的交易日历及交易状态，不能仅凭两条日期差作结论。

## 后续换成真实历史样本

新增历史CSV，先核对数据来源、资产代码、时区/交易日、价格单位、收盘/复权字段及公司行动处理。
明确选择统一口径后，将对应列整理为asset/date/price，检查重复键与缺失，再复用排序分组流程。
不要直接把当前三天教学日历用于真实市场。当前教程只验证模拟样本，不声称完成真实行情验证。

## 官方方法查阅

- [Pandas 2.3 pct_change](https://pandas.pydata.org/pandas-docs/version/2.3/reference/api/pandas.Series.pct_change.html)
- [Pandas 2.3 分组shift](https://pandas.pydata.org/pandas-docs/version/2.3/reference/api/pandas.core.groupby.DataFrameGroupBy.shift.html)
- [Pandas 2.3 分组pct_change](https://pandas.pydata.org/pandas-docs/version/2.3/reference/api/pandas.core.groupby.DataFrameGroupBy.pct_change.html)

你提供的无版本官方链接可能显示更新版；本教程按已安装的Pandas 2.3.3验证，不需要为本课升级环境。

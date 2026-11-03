# D12 实操：左连接与独立数据流程

学习日期：2026-10-25。建议知识复习20分钟、合并实验45～60分钟、独立流程45～60分钟、两数之和30～45分钟、笔记15分钟。

## 从哪里开始

先读 knowledge.md，再打开 practice.ipynb 写自己的代码。卡住时对照 reference.ipynb。
第7节关闭所有示例，完成一次独立流程；写完后再核对。

```powershell
# & 执行启动文件，使用已有的D盘Python和Jupyter配置。
& "D:\Learning\Start-Jupyter.cmd"
```

浏览器进入d12，右上角内核选Python (D Learning)，Shift+Enter运行，Ctrl+S保存。
Jupyter已打开时刷新文件列表即可。在VS Code里也可打开D:/Learning/study/d12使用同样内核。

## 文件用途

| 文件 | 用途 |
|---|---|
| knowledge.md | 今日知识点总结 |
| practice.ipynb | 你自己的实操代码、独立检查和算法练习 |
| reference.ipynb | 按步骤解释的完整中文注释参考 |
| data/prices.csv | 沿用D11的八行教学样本，编号105价格缺失 |
| data/asset_names.csv | 正常映射，A/B/C各一行 |
| data/asset_names_duplicate.csv | 故意重复A的映射，A/B/C/A |
| outputs/prices_with_names.csv | 正常补名的八行明细，六列 |
| outputs/asset_summary_with_names.csv | 独立流程筛选后生成的两行汇总，八列 |
| pipeline.py | 完整独立流程参考脚本 |
| notes.md | 十五道问答题 |
| notes_reference.md | 单独保存的问答参考 |
| D:/Learning/study/cs61A/1.py | 两数之和参考与六组样例，集中复习 |

映射名称“资产A/B/C”是教学标签，价格也只是样本数值，未指定货币单位。
价格表只含A/B，右侧C用来说明left不会凭空新增右侧资产记录。
以下步骤在同一个Notebook中从上到下执行。每次先写出预期行数，再运行。


## 1. 读取价格并检查

D12 的价格文件与 D11 的教学样本相同：8 行 5 列，A、B 各四条；编号 105 的价格缺失。
本次不修改 D11 文件。read_csv 使用默认缺失识别，空价格读入为 NaN。
先确认价格为数值、日期为日期类型，再检查缺失。
运行前预测：shape=(8,5)，price 缺失 1 个，date 与 asset 不缺失。


```python
from pathlib import Path  # Path：表示和拼接文件路径
import pandas as pd  # pandas 表格处理库，通常简称 pd

base_dir = Path("D:/Learning/study/d12")  # D12 文件夹的绝对路径
prices = pd.read_csv(base_dir / "data" / "prices.csv")  # 读取八行价格记录
prices["price"] = pd.to_numeric(prices["price"], errors="coerce")  # 转换数值，失败变缺失
prices["date"] = pd.to_datetime(  # 转换日期类型
    prices["date"],  # 读取原始日期列
    format="%Y-%m-%d",  # 按 年-月-日 解析
    errors="coerce",  # 非法日期变成 NaT
)  # 转换结果放回 date 列

print(prices)  # 查看原始八条记录
print(prices.shape)  # 预计 (8, 5)
prices.info()  # 查看列类型和非空数量
print(prices.isna().sum())  # 预计 price 缺失 1 个，其他列为 0
```


## 2. 自己建立资产名称映射表

映射表的一行描述一个资产代码对应的名称。asset 是代码，asset_name 是名称。
右表加入 C，但价格左表只有 A、B：用来观察左连接不会因为右表有 C 就新增 C 的价格记录。
本节先用 DataFrame 自己建立映射表，再与准备好的 CSV 比较。
正常映射必须让每个资产代码唯一；本次名称也都非空。
equals 比较对应标签、数据和列类型是否相同，返回一个 True 或 False；不是逐元素比较表。


```python
asset_names = pd.DataFrame({  # 用字典建立名称映射表，每个键是一列的列名
    "asset": ["A", "B", "C"],  # 三个资产代码，每个代码出现一次
    "asset_name": ["资产A", "资产B", "资产C"],  # 与代码逐行对应的名称
})  # 建立三行两列的 DataFrame

provided_names = pd.read_csv(base_dir / "data" / "asset_names.csv")  # 读取已提供的映射文件
print(asset_names)  # 观察代码和名称之间的对应关系
print(asset_names.shape)  # 预计 (3, 2)
print(asset_names.equals(provided_names))  # 检查自己建立的表与文件内容一致，预计 True
print(asset_names["asset"].duplicated().any())  # 是否有重复代码，预计 False
```


## 3. 正常左连接：补充名称

本次连接键是 asset：价格记录的代码与映射表的代码相同，就把名称补过来。
价格日期、行号和 record_id 都不是这次的连接键。
validate="many_to_one" 允许左表一个资产有多条价格，要求右表每个资产只有一条映射。
indicator=True 增加 _merge 检查列：both 代表两边匹配，left_only 代表仅左边有该键。
many_to_one 只验证键的唯一性，不保证每个左侧代码都能找到名称。

运行前预测：8 行仍是 8 行；多出 asset_name 和 _merge 两列，shape=(8,7)。
C 只在右表，左连接结果不新增 C。


```python
named_prices = pd.merge(  # 按共同字段合并两张表
    prices,  # 左表：八条价格记录
    asset_names,  # 右表：资产名称映射
    on="asset",  # 连接键：asset 列
    how="left",  # 左连接，保留左表的资产记录
    validate="many_to_one",  # 检查右表每个连接键最多一行
    indicator=True,  # 增加 _merge 列，显示记录的匹配情况
)  # 结果保存在 named_prices，自定义变量名

print(named_prices)  # 所有 A、B 记录都应有名称，_merge 为 both
print("合并前后行数：", len(prices), len(named_prices))  # 预计 8、8
print("合并后形状：", named_prices.shape)  # 预计 (8, 7)
print(named_prices["_merge"].value_counts())  # both 为 8，未匹配为 0
```


## 4. 临时移除 B 映射，观察未匹配值

在副本中去掉 B 的名称映射，原来的 asset_names 保留。
左连接仍保留 B 的四条价格记录，只是右侧提供的名称缺失，_merge 为 left_only。
这里未匹配不能解释成“B 没有价格”。它说明名称映射中没有 B。
一般情况下，名称本身也可能为空，判断是否匹配时用 _merge 更直接。


```python
names_without_b = asset_names.loc[asset_names["asset"] != "B"].copy()  # 临时只留下 A、C 映射
unmatched_prices = pd.merge(  # 故意使用缺少 B 的映射表
    prices,  # 左表仍有 A、B 共八条价格记录
    names_without_b,  # 右表缺少 B
    on="asset",  # 按资产代码匹配
    how="left",  # 保留价格左表的所有记录
    validate="many_to_one",  # 右表键仍唯一，因此这个检查会通过
    indicator=True,  # 用 _merge 精确观察哪些键没匹配
)  # 得到有四条名称缺失的明细表

unmatched_mask = unmatched_prices["_merge"] == "left_only"  # 标记未找到右侧映射的行
print(unmatched_prices.loc[unmatched_mask])  # 应看到 B 的四条记录
print("结果行数：", len(unmatched_prices))  # 仍然是 8
print("未匹配行数：", int(unmatched_mask.sum()))  # 预计 4
```


## 5. 故意重复 A 映射，观察行数展开

将正常映射中的第一条 A 完整复制一次，形成 A、B、C、A 四行。
iloc[[0]] 的内层 [0] 是行位置列表，因此保留 DataFrame 的二维形状 (1,2)；
iloc[0] 则取得一个 Series。这里要纵向拼接两张表，所以使用 iloc[[0]]。
concat 默认按行拼接；ignore_index=True 为拼接后的映射表生成连续数字索引。

这一次为了观察重复键的结果，先不加 validate。
左侧四条 A 每条匹配右侧两条 A，因此 A 变成八行；B 仍四行，总共十二行。
名称文字相同也会产生两个匹配，不会自动去重。


```python
first_mapping = asset_names.iloc[[0]].copy()  # 复制第一条 A，保留一行两列的表格形状
duplicate_names = pd.concat(  # 将多余映射追加到正常映射后面
    [asset_names, first_mapping],  # 按顺序拼接正常三行和复制的一行
    ignore_index=True,  # 重新生成 0、1、2、3 的默认索引
)  # 映射顺序变成 A、B、C、A

print(duplicate_names)  # 观察 A 的两条相同映射
provided_duplicate = pd.read_csv(base_dir / "data" / "asset_names_duplicate.csv")  # 读取准备的重复样本
print(duplicate_names.equals(provided_duplicate))  # 预计 True

expanded_prices = pd.merge(  # 本次先观察右表重复键的实际匹配结果
    prices,  # 左侧 A 四行、B 四行
    duplicate_names,  # 右侧 A 两行、B 一行、C 一行
    on="asset",  # 仍按资产代码匹配
    how="left",  # 左连接也可能因为右侧重复而增加行数
)  # 不加 validate，仅用于这次重复映射实验

print("合并前后行数：", len(prices), len(expanded_prices))  # 预计 8、12
print(expanded_prices.groupby("asset").size())  # A 为 8，B 为 4
print(expanded_prices.loc[expanded_prices["record_id"] == 101])  # 编号 101 出现两次
```


## 6. 验证映射关系，再修复完全重复副本

validate="many_to_one" 会检查右侧连接键是否唯一，发现重复时抛出 MergeError。
本节故意捕获这个已知问题，让你看到说明后继续学习；正常流程不应忽略未解释的错误。
try 中先尝试合并；如果出现指定的 MergeError，就执行 except 中的说明。

这里已确认 A 的两条映射在代码和名称上完全相同，所以只移除完全重复的映射副本。
如果同一个代码对应不同名称，需要核实来源；不要随意 drop_duplicates("asset") 保留一个。


```python
try:  # 尝试验证这份故意有重复键的映射
    pd.merge(  # 右表 A 代码重复，因此合并验证将失败
        prices,  # 左表：价格记录
        duplicate_names,  # 右表：有重复 A 的映射
        on="asset",  # 连接键为 asset
        how="left",  # 使用左连接
        validate="many_to_one",  # 要求右侧 asset 唯一
    )  # 预计抛出 MergeError，转到下面的 except
except pd.errors.MergeError:  # 只处理本节预期的合并关系错误
    print("预期检查：右侧映射键重复，需要先核实和处理。")  # 输出原因，未生成合格的合并结果

fixed_names = duplicate_names.drop_duplicates(  # 只移除内容完全相同的映射副本
    subset=["asset", "asset_name"],  # 代码和名称都相同，才视为完全重复
    keep="first",  # 相同内容保留第一次出现的那条
).copy()  # 用副本继续操作

fixed_prices = pd.merge(  # 修复之后再次验证合并
    prices,  # 原来的八条价格记录
    fixed_names,  # 已移除完全相同副本的映射
    on="asset",  # 根据资产代码匹配
    how="left",  # 保留价格记录
    validate="many_to_one",  # 重新检查右表键唯一，不只看行数
)  # 本例检查通过，恢复八行
print("修复后映射形状：", fixed_names.shape)  # 预计 (3, 2)
print("修复后明细行数：", len(fixed_prices))  # 预计 8
```


## 7. 关掉示例，独立跑通六步流程

先关闭本参考文件，转到 practice.ipynb 的“独立检查”单元格，从空白写起。
任务：重新读取价格和正常映射；转换价格与日期并检查；筛选资产 A/B、价格非空且至少 100；
按资产统计记录数、非空价格数、起止日期、最高价、最低价；左连接名称；保存 CSV。
写完并解释每一步后，再打开以下参考答案。

预期流程：读取 8 行，筛选后 7 行，分组后 2 行，合并名称后仍 2 行，最终 8 列。
编号 105 已被筛掉，因此本流程 A 的 size=count=3；D11 保留缺失行时为 4/3。
B 为 4/4。日期范围均为 2026-10-12 到 2026-10-15，A 最高/最低 108/100，B 为 205/198。


```python
prices_check = pd.read_csv(base_dir / "data" / "prices.csv")  # 从文件重新读取价格，不依赖前面实验的变量
names_check = pd.read_csv(base_dir / "data" / "asset_names.csv")  # 读取正常、键唯一的名称映射表

prices_check["price"] = pd.to_numeric(  # 将价格转换为数值
    prices_check["price"],  # 需要转换的价格列
    errors="coerce",  # 无法转换的价格变成缺失值
)  # 转换结果写回价格列
prices_check["date"] = pd.to_datetime(  # 将日期转换为日期类型
    prices_check["date"],  # 需要转换的日期列
    format="%Y-%m-%d",  # 按 年-月-日 解析
    errors="coerce",  # 非法日期变成 NaT
)  # 转换结果写回日期列

print("读取后形状：", prices_check.shape)  # 预计 (8, 5)
print(prices_check.isna().sum())  # 价格缺失 1 个，其他列缺失 0 个
print("映射键是否重复：", names_check["asset"].duplicated().any())  # 预计 False

selection = (  # selection：记录每一行是否符合本次筛选要求的布尔 Series
    prices_check["asset"].isin(["A", "B"])  # 资产必须是 A 或 B；isin 表示是否属于给定列表
    & prices_check["price"].notna()  # 价格必须非空；notna 表示不是缺失值
    & (prices_check["price"] >= 100)  # 价格至少为 100；组合条件时给比较式加括号
)  # 三个条件都成立时，整行标记才为 True
filtered = prices_check.loc[selection].copy()  # 保留满足条件的记录，并创建独立副本
print("筛选后形状：", filtered.shape)  # 预计 (7, 5)，编号 105 被排除

summary = filtered.groupby(  # 在筛选结果上按资产分组
    "asset",  # 分组键为资产代码
    as_index=False,  # 让 asset 仍是普通列，方便随后 merge
).agg(  # 一次计算六项统计，并给结果列命名
    record_count=("price", "size"),  # 筛选后每组记录数：A 为 3，B 为 4
    valid_price_count=("price", "count"),  # 非空价格数：A 为 3，B 为 4
    start_date=("date", "min"),  # 每组最早日期
    end_date=("date", "max"),  # 每组最晚日期
    highest_price=("price", "max"),  # 每组最高价
    lowest_price=("price", "min"),  # 每组最低价
)  # 汇总后预计两行七列

final_summary = pd.merge(  # 给汇总表补充资产名称
    summary,  # 左表：按资产汇总的两行
    names_check,  # 右表：资产代码与名称映射
    on="asset",  # 按共同的 asset 列匹配
    how="left",  # 保留左表中 A、B 的汇总结果
    validate="many_to_one",  # 检查右表每个资产代码最多一行
)  # 结果预计两行八列，新增一列 asset_name
print(final_summary)  # 查看最终汇总表
print("合并前后行数：", len(summary), len(final_summary))  # 预计 2、2

output_dir = base_dir / "outputs"  # 设置输出文件夹
output_dir.mkdir(parents=True, exist_ok=True)  # 上级目录也可创建；已存在时继续
report_path = output_dir / "asset_summary_with_names.csv"  # 拼接报告文件路径
final_summary.to_csv(  # 导出本次独立流程的最终结果
    report_path,  # 输出到指定报告文件
    index=False,  # 不保存额外的默认行索引
    encoding="utf-8-sig",  # 使用便于 Windows 软件识别的 UTF-8 编码
    date_format="%Y-%m-%d",  # 日期输出为 年-月-日
)  # 报告保存完成
print("最终报告：", report_path)  # 显示结果文件的位置
```


## 8. 保存正常左连接明细，保留主流程结果

将第 3 节正常映射得到的八行明细保存下来，方便复习。
_merge 只是本次检查用的辅助列，导出明细时移除；asset_name 仍保留。
outputs/prices_with_names.csv 是未筛选的八行明细，包含编号 105 的空价格；
outputs/asset_summary_with_names.csv 是第 7 节筛选七行后得到的两行汇总。
两个文件用途不同，不要把明细的八行和汇总的两行直接比较成“少了六条”。


```python
output_dir = base_dir / "outputs"  # 指定结果文件夹
output_dir.mkdir(parents=True, exist_ok=True)  # 必要时创建目录，已存在则继续
detail_for_export = named_prices.drop(columns=["_merge"])  # 去掉检查辅助列，不改 named_prices
detail_path = output_dir / "prices_with_names.csv"  # 拼接正常左连接明细的文件路径
detail_for_export.to_csv(  # 保存八行、六列的明细表
    detail_path,  # 输出路径
    index=False,  # 不保存默认数字索引
    encoding="utf-8-sig",  # 使用便于 Windows 识别的编码
    date_format="%Y-%m-%d",  # 日期按 年-月-日 写出
)  # 明细保存完成
print("正常左连接明细：", detail_path)  # 显示文件位置
print(detail_for_export.shape)  # 预计 (8, 6)
```


## 9. 两数之和：先找之前的搭档，再记录当前元素

本题返回下标，不是两个数值；下标从 0 开始，同一个下标不能用两次。
[5,5] 的两个 5 分别位于下标 0、1，可以一起使用。
seen 是字典，保存之前出现的“数值: 下标”；与第 217 题的集合不同，今天需要保存位置。
enumerate 同时提供当前下标和数值，needed 是 target-number。
先查 seen，再写入当前元素，因此找到的下标一定在当前元素之前，不会把自己配给自己。

[5,5]、目标 10：第一轮 seen={}，找不到 5，存成 {5:0}；
第二轮查到之前的 5，对应下标 0，于是返回 [0,1]。
算法平均时间 O(n)、最坏额外空间 O(n)，这里字典单次查找和写入按平均 O(1) 分析。


```python
def two_sum(nums, target):  # nums 是数字列表，target 是目标和；返回两个不同的下标
    seen = {}  # 空字典；保存“之前出现的数值: 对应下标”，不是空集合

    for index, number in enumerate(nums):  # enumerate 同时给出下标和数值；下标从 0 开始
        needed = target - number  # needed：当前数字还需要配上多少，才能得到目标和

        if needed in seen:  # 在字典的键中，检查所需数值是否已经在前面出现
            return [seen[needed], index]  # 返回之前的下标和当前下标，两者一定不同

        seen[number] = index  # 没有找到搭档，才把当前数值及下标存入字典

    return []  # 本地扩展：没找到解时返回空列表；原题保证有唯一解

examples = [  # 每项保存：输入列表、目标和、预期返回的下标
    ([5, 5], 10, [0, 1]),  # 数值相同但下标不同，是合法答案
    ([3, 2, 4], 6, [1, 2]),  # 不能把第一个 3 与自身配成 6
    ([2, 7, 11, 15], 9, [0, 1]),  # 普通情况：前两个数相加为 9
    ([0, 4, 3, 0], 0, [0, 3]),  # 两个零分别位于下标 0 和 3
    ([-3, 4, 3, 90], 0, [0, 2]),  # 负数与正数也能配对
    ([3], 6, []),  # 本地扩展：只有一个元素，不能返回 [0, 0]
]  # 测试样例定义完毕

for nums, target, expected in examples:  # 每轮取出一组输入、目标和与预期答案
    answer = two_sum(nums, target)  # 调用函数，取得返回的下标列表
    print(nums, "目标：", target, "结果：", answer)  # 查看每组实际结果
    assert answer == expected  # assert：结果与预期不同则停止，便于检查

print("两数之和六组检查通过。")  # 全部样例符合预期才会执行到这里
```


## 最终独立流程的预期结果

| asset | record_count | valid_price_count | start_date | end_date | highest_price | lowest_price | asset_name |
|---|---:|---:|---|---|---:|---:|---|
| A | 3 | 3 | 2026-10-12 | 2026-10-15 | 108 | 100 | 资产A |
| B | 4 | 4 | 2026-10-12 | 2026-10-15 | 205 | 198 | 资产B |

## 运行参考脚本

```powershell
# 完整数据流程：不需要终端当前目录位于d12，脚本会按自身位置找数据。
& "D:\py\Python3\python.exe" "D:\Learning\study\d12\pipeline.py"

# 两数之和：运行集中复习目录中的参考实现与六组样例。
& "D:\py\Python3\python.exe" "D:\Learning\study\cs61A\1.py"
```

## 完成标准

- 能说清连接键asset的含义，知道名称缺失与价格缺失是两个不同问题。
- 能解释正常8行、缺映射仍8行、重复映射变12行的原因。
- 关闭示例后独立完成六步流程，得到2行8列的汇总并保存。
- 能解释[5,5]为什么可以返回[0,1]，以及为什么不能重复使用同一下标。
- 保存自己的practice.ipynb，回答notes.md，再核对notes_reference.md。

## 常见问题

NameError：先运行定义变量的前面单元格。重启内核后从第一格重新执行。

MergeError：先查看右表asset是否重复。本次第6节是有意演示；实际独立流程要用正常映射。

KeyError：检查列名拼写，用print(df.columns)查看实际列名；本次是asset和asset_name。

名称列全缺失：检查连接键类型、大小写、空格及实际取值，不能仅把缺失名称填成任意名称。

正常明细价格仍有NaN：编号105本来就缺价格，补名称不会补出价格，属于本次预期。

运行pipeline.py只生成汇总：八行明细在Notebook第8节生成；两个入口用途在文件说明中分别列出。

## 查阅

[Pandas merge官方文档](https://pandas.pydata.org/pandas-docs/version/2.3/reference/api/pandas.merge.html)
解释how、on、indicator和validate。
[两数之和原题](https://leetcode.com/problems/two-sum/description/)
要求返回两个不同下标，并保证原题有唯一答案。

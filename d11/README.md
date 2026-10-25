# D11：Pandas 分组与聚合实操

学习日期：2026-10-25。建议实操 90～120 分钟，另留 15～20 分钟回答笔记题。

目标：按资产统计记录数、非空价格数、起止日期、最高价和最低价；用 agg 整理为一张汇总表，手算 A 核对。

## 今天先打开哪个文件

1. 在 PowerShell 输入下面的启动命令，或双击 D:/Learning/Start-Jupyter.cmd。
2. 浏览器文件列表进入 d11，打开 practice.ipynb；右上角选择 Python (D Learning)。
3. 按任务顺序在空白代码单元格里写代码。需要帮助时另开 reference.ipynb，按相同编号对照。
4. Shift+Enter 运行当前单元格，Ctrl+S 保存文件。重新启动内核后，需要从第一格开始运行。
5. 完成后回答 notes.md，写好再查看 notes_reference.md。

```powershell
# & 表示执行后面的启动文件；这个启动器会使用 D 盘的 Python 和 Jupyter 配置。
& "D:\Learning\Start-Jupyter.cmd"
```

如果浏览器里已经开着 Jupyter，刷新文件列表即可看到 d11，不用重复启动。
在 VS Code 中也可以打开 D:/Learning/study/d11，选择同样的内核运行 Notebook。

## 文件说明

| 文件 | 用途 |
|---|---|
| practice.ipynb | 你自己的练习代码与输出，主线文件 |
| reference.ipynb | 按步骤拆开的参考答案，代码附中文注释 |
| data/prices.csv | 本次练习样本：八行，编号 105 的价格缺失 |
| data/prices_original.csv | D9 原始八行副本，保留编号 105 的原价格 102 |
| outputs/asset_summary.csv | 参考流程生成的两行汇总表；你运行练习后会更新它 |
| notes.md | 十二道问答题，记录自己的解释 |
| notes_reference.md | 单独保存的问答参考答案 |
| aggregate_prices.py | 可直接运行的完整参考脚本，供之后复习 |

## 本次数据怎么来的

来自 D9 的 data/prices.csv，只复制到 D11。教学副本仅将编号 105 的 price 从 102 留空。
一行代表一个资产在一天的一条价格记录，价格使用样本数值，未指定货币单位；volume 为样本成交量。
原样本有两个资产，各四天：

| 日期 | A 的价格 | B 的价格 |
|---|---:|---:|
| 2026-10-12 | 100 | 200 |
| 2026-10-13 | 105 | 198 |
| 2026-10-14 | 缺失 | 205 |
| 2026-10-15 | 108 | 203 |

D11 的 A 有四条记录、一条空价格；D10 清洗后的 A 只有三条记录。
本次直接使用已准备的 D11 教学样本，不需要重做 D10 的清洗任务。
今天先保留空价格记录，观察 size 与 count 的区别，不删除该行，也不填零。

## 预期结果

| asset | record_count | valid_price_count | start_date | end_date | highest_price | lowest_price |
|---|---:|---:|---|---|---:|---:|
| A | 4 | 3 | 2026-10-12 | 2026-10-15 | 108 | 100 |
| B | 4 | 4 | 2026-10-12 | 2026-10-15 | 205 | 198 |

其中 record_count 为记录行数；valid_price_count 为转换数值后的非空价格数。
日期范围统计全部记录对应的日期。下面所有步骤都在同一个 Notebook 中从上往下运行。


## 1. 读取 D11 的练习样本

本次只使用 `data/prices.csv`。它有 8 行、5 列，A 与 B 各有四条记录。
这是 D9 原始八行样本的教学副本，只把编号 105 的价格设为空。
`data/prices_original.csv` 保留原来的八行，供追溯；D9、D10 的文件没有被修改。

本例使用 `read_csv` 默认设置，CSV 中的空字段会识别为缺失值。
不要沿用 D10 的 `keep_default_na=False`：D10 当时需要保留原始文字，今天直接统计非空数。
代码采用 D11 的绝对路径，因此终端当前处于 `D:/Learning` 或项目根目录都能找到样本。
运行前预测：`df.shape` 应为 `(8, 5)`，编号 105 的价格应显示为 `NaN`。


```python
from pathlib import Path  # Path：用于表示、拼接文件和文件夹路径
import pandas as pd  # pandas：表格处理库；pd 是常用简称

base_dir = Path("D:/Learning/study/d11")  # 本次 D11 文件夹的绝对路径
data_path = base_dir / "data" / "prices.csv"  # / 在 Path 之间用于拼接路径
output_dir = base_dir / "outputs"  # 之后保存汇总表的文件夹

df = pd.read_csv(data_path)  # 读取 CSV 为 DataFrame；空价格字段自动识别为缺失
print(df)  # 查看全部八条记录；编号 105 的 price 应为 NaN
print("原表形状：", df.shape)  # shape 是属性，预计输出 (8, 5)
```


## 2. 确认价格和日期的类型

统计最高价、最低价前，让价格成为数值；统计起止日期前，让日期成为日期类型。
`errors="coerce"` 表示无法转换的内容变成缺失值，不能理解成已经修复原数据。
这份教学样本只有一条空价格，没有非法日期、重复记录或价格冲突。

运行前预测：`price` 缺失数为 1，其他列缺失数为 0。
今天的“有效价格数”指完成数值转换后，价格列的非空数量。
`count()` 本身不检查价格是否符合业务规则。


```python
df["price"] = pd.to_numeric(  # 将价格列明确转换为数值类型
    df["price"],  # 指定需要转换的原始价格列
    errors="coerce",  # 无法转成数字的值转为缺失值；已有缺失值仍然缺失
)  # 将转换结果放回 price 列

df["date"] = pd.to_datetime(  # 将日期文字转换为日期类型
    df["date"],  # 指定需要转换的原始日期列
    format="%Y-%m-%d",  # %Y 年、%m 月、%d 日；例如 2026-10-12
    errors="coerce",  # 非法日期转换为 NaT，即日期缺失值
)  # 将转换结果放回 date 列

df.info()  # 查看列、非空数量和类型；直接调用即可，不需要外面再套 print
print(df.isna().sum())  # isna 标记缺失，再逐列计数；预计 price 为 1，其他为 0
```


## 3. 按资产分组，观察 A 组

`grouped` 是自定义变量名，保存 GroupBy 分组对象。
`groupby("asset")` 根据 asset 列的值分组，A 的所有记录归为一组，B 的所有记录归为另一组。
单独分组还没有生成汇总表；原始八行也没有消失。

`ngroups` 表示组数，是属性，因此后面没有括号。
`get_group("A")` 取出 A 组的全部原始记录，是方法，因此需要括号。
运行前预测：有 2 组；A 组形状为 `(4, 5)`；A 的价格为 100、105、缺失、108。


```python
grouped = df.groupby("asset")  # 依据 asset 列分组，得到 GroupBy 对象
print("资产组数：", grouped.ngroups)  # ngroups 是组数，预计输出 2

a_records = grouped.get_group("A")  # 提取 asset 等于 A 的四条记录
print(a_records)  # 显示 A 组全部记录，包括价格缺失的那一行
print("A 组形状：", a_records.shape)  # 仍有四行五列，预计为 (4, 5)
```


## 4. 先分别计算六项统计

`size()` 统计每组的行数，价格缺失的记录仍算一行。
`grouped["price"].count()` 统计每组 price 列的非空值数量。
`grouped["price"]` 表示在每个资产组内，选择价格列继续计算。

运行前预测：A 的记录数 4、非空价格数 3；B 的两项都是 4。
价格的 min/max 忽略缺失值。这里日期范围覆盖各资产的全部记录，未先删掉空价格行。
本例日期完整；若整组价格都缺失，最高价与最低价也会缺失，不应改成 0。


```python
record_counts = grouped.size()  # 统计每个资产组的记录行数，含空价格行
valid_price_counts = grouped["price"].count()  # 统计每组非空价格数
start_dates = grouped["date"].min()  # 每组最早日期；不需要先按日期排序
end_dates = grouped["date"].max()  # 每组最晚日期
highest_prices = grouped["price"].max()  # 每组最高价，忽略价格缺失值
lowest_prices = grouped["price"].min()  # 每组最低价，忽略价格缺失值

print("记录数：", record_counts)  # A 为 4，B 为 4
print("非空价格数：", valid_price_counts)  # A 为 3，B 为 4
print("起始日期：", start_dates)  # A、B 都是 2026-10-12
print("结束日期：", end_dates)  # A、B 都是 2026-10-15
print("最高价：", highest_prices)  # A 为 108，B 为 205
print("最低价：", lowest_prices)  # A 为 100，B 为 198
```


## 5. 用 agg 整理成一张汇总表

`agg` 是 aggregate 的简写，意为聚合、汇总。
`as_index=False` 让分组键 asset 保留为结果中的普通列。
下面使用“命名聚合”：`结果列名=(原表列名, 统计方法)`。

例如 `valid_price_count=("price", "count")`：
`valid_price_count` 是自定义的结果列名；`price` 必须是原表已有的列；`count` 是统计方法。
括号中的两个值组成一个元组。
`record_count=("price", "size")` 使用 size，因此价格缺失的那行也计入。

运行前预测：A、B 各输出一行；asset 加六项统计，共 `(2, 7)`。


```python
grouped_for_summary = df.groupby(  # 创建用于整理汇总表的分组对象
    "asset",  # 仍根据资产编号分组
    as_index=False,  # 分组键 asset 保持为普通列，结果使用默认数字索引
)  # 这里尚未执行统计

summary = grouped_for_summary.agg(  # agg：一次完成并命名多项统计
    record_count=("price", "size"),  # 每组记录数，包含空价格行
    valid_price_count=("price", "count"),  # 每组非空价格数
    start_date=("date", "min"),  # 每组最早日期，覆盖全部记录
    end_date=("date", "max"),  # 每组最晚日期，覆盖全部记录
    highest_price=("price", "max"),  # 每组最高价
    lowest_price=("price", "min"),  # 每组最低价
)  # 每组整理成一行；结果保存到 summary

print(summary)  # 查看 A、B 两行汇总结果
print("汇总表形状：", summary.shape)  # 预计输出 (2, 7)
```


## 6. 手算 A，并逐项核对

先在纸上写答案，再运行本节。不要把程序输出直接抄成“手算结果”。

A 的四条记录日期是 10 月 12、13、14、15 日，价格是 100、105、缺失、108。
所以记录数为 4，非空价格数为 3，最高价为 108，最低价为 100；
起止日期为 2026-10-12 和 2026-10-15。
即使 10 月 14 日价格缺失，那条记录仍属于 A 组。

以下字典保存独立手写的预期值。
`pd.Timestamp` 用于把一个日期文字表示为单个 Pandas 日期值，方便与统计结果比较。
临时用 set_index 把 asset 作为索引，再 loc["A"] 取到 A 的一行统计，不修改原 summary。
这次取单行得到 Series，其索引是六项统计字段。


```python
manual_a = {  # 字典：保存从纸上独立手算得到的 A 组答案
    "record_count": 4,  # 四条记录，其中一条价格缺失
    "valid_price_count": 3,  # 只有三个价格不是缺失值
    "start_date": pd.Timestamp("2026-10-12"),  # 最早日期
    "end_date": pd.Timestamp("2026-10-15"),  # 最晚日期
    "highest_price": 108,  # 非空价格 100、105、108 中的最大值
    "lowest_price": 100,  # 非空价格 100、105、108 中的最小值
}  # 字典创建完成

summary_by_asset = summary.set_index("asset")  # 返回以资产为索引的新表
a_summary = summary_by_asset.loc["A"]  # 按标签 A 取出该行，得到一个 Series

for field, expected in manual_a.items():  # 每次取出一个字段名和对应手算值
    actual = a_summary[field]  # 按字段名读取程序统计出的实际值
    print(field, "程序：", actual, "手算：", expected)  # 并列查看两种结果
    assert actual == expected  # assert：实际值不相等时停止并报错，帮助发现问题

print("A 组的六项统计与手算一致。")  # 前面六项全部相等才会执行到这里
```


## 7. 导出汇总表，并检查总数

保存到 `outputs/asset_summary.csv`。重复运行会更新这个结果文件。
`index=False` 表示不把表左侧的默认数字索引另写成一列，asset 作为普通列仍会保存。
`utf-8-sig` 是带标记的 UTF-8 编码，方便 Windows 软件识别中文。
`date_format` 控制导出的日期写法。CSV 保存文字和数值内容，不保留 Pandas 的列类型。

运行前预测：记录数合计 8，非空价格数合计 7。
汇总表只有两行，因为有 A、B 两个资产组，每组的六项统计聚合成一行。
不是只保留了两条原始记录，原始 df 仍然有八行。


```python
output_dir.mkdir(  # 创建保存结果的文件夹
    parents=True,  # 上级文件夹不存在时一并创建
    exist_ok=True,  # 文件夹已经存在时继续执行
)  # 此时输出文件夹已准备好

summary_path = output_dir / "asset_summary.csv"  # 拼接结果文件的完整路径
summary.to_csv(  # 将汇总表写成 CSV 文件
    summary_path,  # 输出文件路径
    index=False,  # 不输出额外的默认索引列；asset 普通列仍保留
    encoding="utf-8-sig",  # 采用带标记的 UTF-8 编码
    date_format="%Y-%m-%d",  # 日期输出为例如 2026-10-12
)  # CSV 保存完成

print("结果保存位置：", summary_path)  # 显示刚保存的结果路径
print("记录数合计：", summary["record_count"].sum())  # 预计为 8
print("非空价格数合计：", summary["valid_price_count"].sum())  # 预计为 7
print("原表仍有多少行：", len(df))  # 原表仍为八行，聚合不会删除原表记录
```


## 8. 独立验收与保存

- 在 practice.ipynb 中不看参考重写 agg，并得到两行七列。
- 口头解释 A 的记录数为什么是 4，非空价格数为什么是 3。
- 解释两行各代表一个资产组；原表仍有八行。
- 检查输出 CSV：有 asset 列，没有额外的 Unnamed: 0 列。
- 回答 notes.md；然后再打开 notes_reference.md 核对。
- 在 Jupyter 按 Ctrl+S；或在 VS Code 保存所有已修改文件。

选做：对 summary.copy() 的副本新增 missing_price_count，计算 record_count-valid_price_count。
预计 A 为 1、B 为 0，主汇总继续保持七列。

完整参考脚本的运行方式如下。它会打印结果并更新 outputs/asset_summary.csv，不会替你填写练习 Notebook。

```powershell
# & 执行指定的 Python；后面的路径是要运行的脚本，当前目录可以不在 D11。
& "D:\py\Python3\python.exe" "D:\Learning\study\d11\aggregate_prices.py"
```

脚本用 Path(__file__).resolve().parent 找到自己所在的文件夹；__file__ 不适用于 Notebook 的普通代码单元格。

## 常见问题

**FileNotFoundError（找不到文件）**：核对读取路径是否指向 D11/data/prices.csv，以及文件名是否准确。

**NameError（名称未定义）**：通常是跳过了前面的单元格，或重启内核后没重新运行。按顺序从第一格开始执行。

**A 的两种计数都为 4**：可能读了 prices_original.csv；或者把缺失价格填成了 0。主线应读 prices.csv。

**A 的两种计数都为 3**：可能读了 D10 清洗结果，或提前删除了价格缺失行。

**分组结果显示的是数字索引**：本教程使用 as_index=False，asset 是普通列，这是预期行为。

**代码运行了但没有输出**：定义变量不会自动打印。使用本教程的 print 语句查看结果，并确认运行的是正确单元格。

**输出价格显示 108.0**：原价格列含 NaN，通常会使用浮点类型；108.0 与 108 数值相等。

## 官方查阅入口

- [Pandas 2.3 分组指南](https://pandas.pydata.org/pandas-docs/version/2.3/user_guide/groupby.html)
- [size：每组行数](https://pandas.pydata.org/pandas-docs/version/2.3/reference/api/pandas.core.groupby.DataFrameGroupBy.size.html)
- [count：每组非空数量](https://pandas.pydata.org/pandas-docs/version/2.3/reference/api/pandas.core.groupby.DataFrameGroupBy.count.html)
- [agg：命名聚合](https://pandas.pydata.org/pandas-docs/version/2.3/reference/api/pandas.core.groupby.DataFrameGroupBy.agg.html)

# D10：类型、缺失值、日期与重复记录清洗

日期：2026-10-22。

今天使用虚构的资产价格样本练习清洗。完成后，需要能解释：每条异常记录为什么被标记、为什么保留或移出清洗结果，以及如何追溯到原始记录。

## 先解释截图中的代码

截图代码是：

```python
country_grp["LanguageWorkedWith"].apply(
    lambda x: x.str.contains("Python").sum()
)
```

它的整体含义是：**按国家分别统计，语言字段包含 Python 的记录有多少条。**

`country_grp` 通常来自下面这样的分组操作；截图没有显示创建它的那一行：

```python
country_grp = survey.groupby("Country")  # groupby：按 Country 国家列分组
```

逐段理解：

| 代码 | 含义 |
|---|---|
| `country_grp` | 按国家分好组的数据 |
| `["LanguageWorkedWith"]` | 每组只关注语言这一列 |
| `.apply(...)` | 将指定函数分别应用到各个组，再汇总结果 |
| `lambda x: ...` | 定义一个简短的匿名函数，`x` 是传入的参数 |
| `x` | 当前国家那一组的语言数据，是一个 Series，不是一个字符串 |
| `x.str.contains("Python")` | 判断这一组每条记录的文字是否包含 Python，得到 True/False |
| `.sum()` | 把 True 按 1、False 按 0 相加，得到匹配记录数量 |

例如，一组语言文字是：

```text
Python;SQL
JavaScript
Python;Python
```

判断结果为 True、False、True，因此合计为 2。最后一条虽然写了两次 Python，也只算一条匹配记录。结果统计的是**记录数量**，不是子串出现次数。

更稳健的写法是：

```python
python_counts = country_grp["LanguageWorkedWith"].apply(
    lambda x: x.str.contains("Python", na=False, regex=False).sum()
)
```

- `na=False`：缺失内容视为不匹配。
- `regex=False`：按普通文字查找，不把查找内容当作正则表达式。
- 默认区分大小写，Python 与 python 不一定匹配。

也可以用具名函数拆开，先理解每一步：

```python
def count_python(language_series):  # 接收某一个国家的语言 Series
    matches = language_series.str.contains(
        "Python", na=False, regex=False
    )  # 得到这个国家每条记录的布尔判断
    return matches.sum()  # 返回包含 Python 的记录数


python_counts = country_grp["LanguageWorkedWith"].apply(count_python)
```

这里 `apply` 接收的是函数 `count_python`，不写成 `count_python()`；每个组由 Pandas 分别传给这个函数。

## 启动和今天的文件

在 PowerShell 运行：

```powershell
& "D:\Learning\Start-Jupyter.cmd"
```

`&` 是 PowerShell 的调用操作符。浏览器中进入 d10，内核选择 **Python (D Learning)**。按 **Shift + Enter** 运行当前单元格，按 **Ctrl + S** 保存，并从上往下执行。

| 文件 | 用途 |
|---|---|
| `D:/Learning/study/d10/data/prices_dirty.csv` | 加入问题后的教学样本，保留原始文字 |
| `D:/Learning/study/d10/reference.ipynb` | 带中文注释的参考 Notebook |
| `D:/Learning/study/d10/practice.ipynb` | 从空白代码开始独立练习 |
| `D:/Learning/study/d10/clean_prices.py` | 可重复运行的清洗脚本 |
| `D:/Learning/study/d10/notes.md` | 今天的问答题 |
| `D:/Learning/study/d10/outputs/anomalies.csv` | 另存的异常记录，预计 6 行 |
| `D:/Learning/study/d10/outputs/prices_clean.csv` | 清洗结果，预计 7 行 |
| `D:/Learning/study/cs61A/217_review_2026-10-22.py` | 第 217 题参考复习版，包含七组检查 |

## 今天的样本和处理规则

原来的 D9 样本有 8 行，今天在副本中追加 5 行，共 13 行。D9 原始样本保持不变。

原始五列是：`record_id、date、asset、price、volume`。读入时先保留文字原貌：

```python
raw = pd.read_csv(csv_path, dtype="string", keep_default_na=False)
```

- `dtype="string"`：先按文字读取，保留日期和价格原始内容。
- `keep_default_na=False`：读取时保留空字符串等原貌，后面自己分类。
- `raw` 保留原始内容，另建副本处理。

追加的五行分别用于观察空价格、非数字价格、非法日期、完全重复、同资产同日价格冲突。

新增 `source_row` 表示 **CSV 中不包含表头的数据行序号，取值为 1～13**。它用于追溯来源，不是记录编号，也不是从 0 开始的 Pandas 行位置。

### 1. 保留原字段，新增转换字段

不要覆盖原始 `price` 和 `date`。在工作副本中新增：

```python
price_text = work["price"].str.strip()  # 去掉价格文字首尾空白
work["price_clean"] = pd.to_numeric(price_text, errors="coerce")
work["date_clean"] = pd.to_datetime(
    work["date"].str.strip(), format="%Y-%m-%d", errors="coerce"
)
```

- `price_clean`：转换后的数值价格。
- `date_clean`：转换后的日期。
- `errors="coerce"`：转换失败时产生缺失值；不代表原问题已经修好。
- 数值缺失可能显示为 NaN 或 `<NA>`，日期缺失显示为 NaT；统一使用 `isna()` 判断。

### 2. 先分类无效价格和日期

| 问题 | 识别依据 | 本样本对应记录 | 处理理由 |
|---|---|---|---|
| 空价格 | 去空白后的原价格文字为空 | 编号 109，source_row=9 | 无法知道真实价格，不能直接当作零 |
| 非数字价格 | 原价格非空，但 `price_clean.isna()` 为 True | 编号 110，source_row=10 | 文字无法作为数值参与计算，需要保留原始内容核实 |
| 非法日期 | `date_clean.isna()` 为 True | 编号 111，source_row=11 | 例如 2026-02-30 不存在，不能任意猜成另一天 |

空价格和非数字价格都可能在转换后表现为缺失，因此要结合原始文字区分。将三条记录另存到异常结果，剩下 10 条继续检查。

### 3. 检查完全重复，保留一份

完全重复指：**原始五列的内容全部相同**。本样本 source_row=12 完整复制了 source_row=1 的编号 101 记录。

必须明确比较的列，排除新增的 `source_row`、清洗字段和问题标记：

```python
original_columns = ["record_id", "date", "asset", "price", "volume"]

duplicate_mask = valid.duplicated(
    subset=original_columns, keep="first"
)

exact_removed = valid.loc[duplicate_mask].copy()  # 需要移出的多余副本
remaining = valid.loc[~duplicate_mask].copy()  # 保留首次出现的记录
```

新增的 `source_row` 每行都不同，如果把它也用于比较，就无法识别这两条原始内容相同的记录。

理解两个参数值的区别：

- `keep=False`：重复组里的所有成员都标记为 True，包括第一次出现的那条。这里会标记 source_row=1、12，共两行，适合检查重复组。
- `keep="first"`：第一次出现的标记为 False，后续多余副本标记为 True。这里仅标记 source_row=12，共一行，适合保留一份、移出其余副本。

移出一条多余副本后，还剩 9 行。

### 4. 检查同一资产同一天的价格冲突

价格冲突指：**资产相同、日期相同，但有效数值价格不同**。

本样本中，编号 103 与 112 都是资产 A、2026-10-13，但价格分别为 105 和 999；对应 source_row=3、13。

可以这样检查：

```python
price_count = remaining.groupby(
    ["asset", "date_clean"]
)["price_clean"].transform("nunique")

conflict_mask = price_count > 1
conflicts = remaining.loc[conflict_mask].copy()
clean = remaining.loc[~conflict_mask].copy()
```

- `groupby(["asset", "date_clean"])`：按“资产＋日期”分组。
- `nunique`：数一数每组有多少个不同的有效价格。
- `transform("nunique")`：把每组的数量对应回各行，结果与当前表的行数、索引对应。
- `> 1`：同一资产同一天存在不止一个价格，因此将该组标记为冲突。

同资产同日期出现多行，不一定是价格冲突；关键是价格是否不同。

对这个冲突组，两行都移到异常结果等待核实，不能凭 `first` 或 `last` 擅自决定保留哪个价格。这里只是隔离待核实，不代表已经判断 105 或 999 哪个真实。

### 5. 导出并核对总数

异常结果应包含：

- 无效价格或日期：3 行。
- 移出的完全重复副本：1 行。
- 价格冲突组：2 行。

因此：

```text
原始 13 行 = 清洗结果 7 行 + 无效记录 3 行 + 多余重复副本 1 行 + 价格冲突 2 行
```

| 检查阶段 | 本阶段移出的行数 | 继续处理的行数 |
|---|---:|---:|
| 原始副本 | 0 | 13 |
| 无效价格、日期 | 3 | 10 |
| 完全重复副本 | 1 | 9 |
| 价格冲突 | 2 | 7 |

`anomalies.csv` 预计为 6 行，保留来源编号、原始内容和异常说明。`prices_clean.csv` 预计为 7 行，同样保留 `source_row` 方便追溯。

清洗结果的记录编号为：101、102、104、105、106、107、108。检查时关注编号集合，不把导出的显示顺序当作记录身份。

导出使用：

```python
anomalies.to_csv(anomalies_path, index=False, encoding="utf-8-sig")
clean.to_csv(clean_path, index=False, encoding="utf-8-sig")
```

`index=False` 表示不额外导出 Pandas 行索引；`source_row` 是有意义的数据列，会保留下来。CSV 不保存 Pandas 的类型信息，重新读取后仍应检查日期和数值类型。

需要重复运行清洗脚本时，在 PowerShell 输入：

```powershell
& "D:\py\Python3\python.exe" "D:\Learning\study\d10\clean_prices.py"
```

建议先在 `practice.ipynb` 独立完成，再与参考 Notebook、脚本和导出结果对照。

## 第 217 题复习与复杂度

函数用集合 `seen` 保存已经见过的数字：每次先检查 `number in seen`，发现重复立即返回 True，未出现过才调用 `seen.add(number)`。全部检查完仍无重复，才在循环外返回 False。

- 集合查找和添加的平均时间为 O(1)。
- 最多检查 n 个数字，因此整体平均时间复杂度为 O(n)。n 是输入列表的长度。
- 最坏额外空间为 O(n)，例如所有数字都不重复，需要将它们全部记录下来。
- 可以提前返回：全相同且至少有两个元素时，检查第二个元素就发现重复，不需要遍历完整列表。

参考文件包含七组：非相邻重复、没有重复、所有值相同、单个数字、负数、零，以及本地拓展的空列表。先在练习中独立实现，再用参考版核对结果。

## 今天的完成标准

1. 能拆解截图中的 apply 和 lambda，说明统计的是记录数。
2. 能用原始文字区分空价格与非数字价格，并说明非法日期的处理方式。
3. 能解释完全重复与价格冲突的区别，以及为什么冲突组不直接保留第一条或最后一条。
4. 异常表 6 行、清洗表 7 行，来源序号没有丢失，没有记录被重复归类或无故消失。
5. 独立复做 217，通过七组检查，并解释平均时间 O(n) 与最坏额外空间 O(n)。

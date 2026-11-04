# D17 实操：SQL连接与Python访问SQLite

学习日期：2026-11-03，对应原计划10.27。今天不加新算法题，优先完成数据库练习。
学习目标：自己建价格表、资产信息表，插入样本，按资产查询并补名称；SQL与Pandas结果一致；关闭后重开仍可查。

## 学习顺序与时间

- 课程与knowledge.md：60～75分钟，重点INNER/LEFT和Python连接、建表、插入、查询。
- 文件库建立、提交与重开验证：35～45分钟。
- JOIN、Pandas核对与重复键演示：50～65分钟。
- 关闭参考独立复写、笔记：20～30分钟。

## 打开练习

```powershell
# &调用已有D盘Jupyter启动器；已打开时刷新文件列表即可。
& "D:\Learning\Start-Jupyter.cmd"
```

进入d17，打开practice.ipynb，内核选Python (D Learning)。Shift+Enter运行，Ctrl+S保存。
每段从上到下执行。SQL放入Python三引号字符串再交给execute/read_sql_query，不直接把裸SQL交给Python。
你自己的库用market_practice.sqlite3，参考库用market_reference.sqlite3，均放在D盘data文件夹。

|文件|用途|
|---|---|
|knowledge.md|知识点、参数和新名称解释|
|practice.ipynb|独立练习留白，自己创建market_practice.sqlite3|
|reference.ipynb|分步骤、逐行中文注释参考|
|schema_reference.sql|两张正式表与演示表的结构|
|queries_reference.sql|指定资产、INNER/LEFT及重复键查询|
|sql_practice.sql|保存自己写的SQL|
|run_sqlite_reference.py|可直接运行的完整参考脚本|
|data/market_reference.sqlite3|已经验证的参考文件数据库|
|outputs/join_results.txt|参考查询输出，便于对照|
|notes.md / notes_reference.md|13道问答与单独答案|

## 样本先看懂

价格表prices：

|record_id|asset|date|price|
|---:|---|---|---:|
|101|A|2026-10-12|100|
|102|A|2026-10-13|110|
|103|A|2026-10-14|99|
|104|B|2026-10-12|200|
|105|B|2026-10-13|190|
|106|C|2026-10-12|50|

信息表asset_info：A→Asset A，B→Asset B，D→Asset D。全部是模拟教学数据。
C只有价格无名称；D只有名称无价格。先预测INNER和LEFT分别会保留谁。
重复演示另用asset_info_demo：A有两个名称，B/D各一个；正式表不变。

|操作|预期|
|---|---|
|指定A并补名称|3行5列，价格100/110/99|
|正式信息INNER JOIN|5行5列，无C|
|正式信息LEFT JOIN|6行5列，C名称缺失|
|重复映射LEFT JOIN|9行6列，A的每条价格有两条匹配|
|最终关闭重开查三张表|价格6、正式信息3、演示信息4|


## 1. 连接D盘文件数据库

今天使用文件数据库，而不是D16的:memory:。文件路径固定，重开时必须使用同一路径。
参考代码使用market_reference.sqlite3；你在practice中使用market_practice.sqlite3，不与参考结果共用文件。
conn是connection连接对象；cur是cursor游标对象，用于执行SQL和读取结果。

以下代码用于自己的练习库：

```python
import sqlite3  # Python自带SQLite接口，不需要再安装数据库服务器
import pandas as pd  # 用于展示SQL结果并完成merge对照
from pathlib import Path  # 用于表示和连接文件路径

base_dir = Path("D:/Learning/study/d17")  # 今天的练习目录
data_dir = base_dir / "data"  # 数据库文件存放目录
data_dir.mkdir(parents=True, exist_ok=True)  # 父文件夹缺少时一起创建，已存在时不报错
db_path = data_dir / "market_practice.sqlite3"  # 这是自己的练习文件，与参考库分开
conn = sqlite3.connect(str(db_path))  # 连接文件数据库；不存在时创建文件，不会自动创建业务表
cur = conn.cursor()  # 创建游标，用于执行下面的SQL
print(db_path)  # 确认数据库实际保存在D盘
```


## 2. 创建价格表和正式资产信息表

prices每行是一条价格记录；asset_info每行是一种资产的信息。
INTEGER为整数，REAL为实数，TEXT为文本；本课日期存为固定格式文本，不引入额外日期类型转换。
PRIMARY KEY是主键：record_id唯一标识价格记录，asset唯一标识正式信息。
价格表里A有多条价格是正常的；正式信息表里同一A出现两个名称则违反本课的唯一约束。

以下代码用于自己的练习库：

```python
cur.execute("""
CREATE TABLE IF NOT EXISTS prices (  -- 表不存在才创建，重复运行不删除已有表
    record_id INTEGER PRIMARY KEY,  -- 每条价格记录的唯一编号
    asset TEXT NOT NULL,  -- 资产代码，允许同一资产有多个日期的价格
    date TEXT NOT NULL,  -- 本课用YYYY-MM-DD格式文本保存日期
    price REAL NOT NULL  -- REAL表示实数；本课小样本价格
);
""")  # execute一次执行一条建表语句

cur.execute("""
CREATE TABLE IF NOT EXISTS asset_info (  -- 正式资产信息表
    asset TEXT PRIMARY KEY NOT NULL,  -- 每个资产代码只允许一条信息，不允许空代码
    asset_name TEXT NOT NULL  -- 资产名称
);
""")  # 正式资产信息表要求资产代码唯一
```


## 3. 批量插入小样本并提交

A有三条价格，B两条，C一条。正式信息表只有A、B、D，故意让C没有名称、D没有价格。
executemany把一条带?占位符的INSERT应用到多行元组，元组元素顺序与字段顺序对应。
本固定教学样本用INSERT OR IGNORE避免重复运行时重复插入同一主键。它不更新已有记录，也不是通用清洗方法。
如果你修改样本但沿用已存在的主键，旧数据会保留。需要独立重做时改用新的数据库文件名，不必删除旧库。

以下代码用于自己的练习库：

```python
price_rows = [  # 每条元组依次是record_id、asset、date、price
    (101, "A", "2026-10-12", 100.0),  # A第一条价格
    (102, "A", "2026-10-13", 110.0),  # A第二条价格
    (103, "A", "2026-10-14", 99.0),  # A第三条价格
    (104, "B", "2026-10-12", 200.0),  # B第一条价格
    (105, "B", "2026-10-13", 190.0),  # B第二条价格
    (106, "C", "2026-10-12", 50.0),  # C在信息表里没有对应名称
]  # 本次共六条模拟价格
info_rows = [("A", "Asset A"), ("B", "Asset B"), ("D", "Asset D")]  # D没有价格记录

cur.executemany(  # 批量执行参数化插入
    "INSERT OR IGNORE INTO prices (record_id, asset, date, price) VALUES (?, ?, ?, ?)",  # 四个值占位符
    price_rows,  # 依次取出每条四元素元组
)  # 固定主键已经存在的记录不会再次添加
cur.executemany(  # 批量插入资产信息
    "INSERT OR IGNORE INTO asset_info (asset, asset_name) VALUES (?, ?)",  # 两个字段对应两个值
    info_rows,  # 每条是代码和名称
)  # 正式信息表初始共三条
conn.commit()  # 提交数据库事务，保存本次写入；不是git commit
```


## 4. 关闭后重开，先验证持久化

不重新建表、不重新插入，直接关闭并重连同一文件，查询两张表。
fetchone返回一条元组，例如(6,)；后面的[0]取其中的数字6。
关闭后原连接和游标都不再使用；新连接需要新游标。commit保存写入，close关闭连接，作用不同。

以下代码用于自己的练习库：

```python
conn.close()  # 关闭当前连接，前一格已经提交写入
conn = sqlite3.connect(str(db_path))  # 重开同一文件；这里没有重新插入数据
cur = conn.cursor()  # 为新连接创建新游标
price_count = cur.execute("SELECT COUNT(*) FROM prices").fetchone()[0]  # 重开后仍应有6条价格
info_count = cur.execute("SELECT COUNT(*) FROM asset_info").fetchone()[0]  # 正式信息仍应有3条
print("重开后价格条数：", price_count, "信息条数：", info_count)  # 预计6和3
assert price_count == 6 and info_count == 3  # 核对数据确实保存在文件中
```


## 5. 参数查询指定资产，并连接名称

p和a只是表别名，可自行命名但整条查询中要一致。p.asset表示价格表的asset列。
ON指定连接匹配条件，WHERE筛选连接结果；本题WHERE使用左表资产字段。
WHERE p.asset = ?中的问号不加引号。参数值另外传入(target_asset,)，末尾逗号表示单元素元组。

以下代码用于自己的练习库：

```python
sql_a = """
SELECT p.record_id, p.asset, p.date, p.price, a.asset_name  -- 选择价格字段和右表名称
FROM prices AS p  -- p是价格表的自定义别名
LEFT JOIN asset_info AS a  -- a是资产信息表别名，保留左侧价格记录
ON p.asset = a.asset  -- 按资产代码匹配，不按行号匹配
WHERE p.asset = ?  -- ?是参数值占位符，不加引号
ORDER BY p.date ASC, p.record_id ASC;  -- 明确按日期、记录编号排序
"""  # 多行SQL字符串，交给SQLite执行
target_asset = "A"  # 想查询的资产代码
cur.execute(sql_a, (target_asset,))  # ?的值由参数元组提供，不把变量直接拼进SQL
asset_rows = cur.fetchall()  # fetchall取出全部结果，得到由行元组构成的列表
print(asset_rows)  # 预计三行，价格100、110、99，都带Asset A名称
```


## 6. 对比INNER JOIN和LEFT JOIN

价格表是左表。INNER JOIN只返回成功匹配的组合，因此没有信息的C被排除，结果五行。
LEFT JOIN保留所有左侧价格记录，C这一行保留而名称为NULL，结果六行。右表独有的D不会自动出现。
LEFT JOIN不是无条件保证行数等于左表；本题右表连接键唯一，所以是六行。重复键演示会打破这个等式。

以下代码用于自己的练习库：

```python
sql_inner = """
SELECT p.record_id, p.asset, p.date, p.price, a.asset_name  -- 从两表选取需要的字段
FROM prices AS p  -- 左表为价格表
INNER JOIN asset_info AS a  -- 仅保留按ON条件能匹配的组合
ON p.asset = a.asset  -- 资产代码相同才匹配
ORDER BY p.record_id ASC;  -- 按记录编号展示
"""  # 多行SQL字符串，交给SQLite执行
sql_left = """
SELECT p.record_id, p.asset, p.date, p.price, a.asset_name  -- 输出五列
FROM prices AS p  -- 左表是价格记录
LEFT JOIN asset_info AS a  -- 保留所有左表记录；右表没有匹配时补NULL
ON p.asset = a.asset  -- 连接条件
ORDER BY p.record_id ASC;  -- 明确结果顺序
"""  # 多行SQL字符串，交给SQLite执行
inner_result = pd.read_sql_query(sql_inner, conn)  # 查询结果读成DataFrame
left_result = pd.read_sql_query(sql_left, conn)  # 结果含C，asset_name缺失
sql_a_result = pd.read_sql_query(sql_a, conn, params=(target_asset,))  # Pandas读SQL时也单独绑定参数
print(inner_result)  # 预计5行5列，只有A和B
print(left_result)  # 预计6行5列，包含无名称的C
print("INNER形状：", inner_result.shape, "LEFT形状：", left_result.shape)  # (5,5)与(6,5)
```


## 7. 用Pandas merge真正重做并核对

分别读取两张原表，再实际执行Pandas merge；不是再次读JOIN结果充当Pandas实现。
validate="many_to_one"检查右表连接键唯一。左侧同资产多条价格允许存在。
SQL未匹配名称可能显示None，Pandas可能显示NaN；统一成string类型后都用pd.NA表示缺失，再比较。

以下代码用于自己的练习库：

```python
prices_df = pd.read_sql_query("SELECT * FROM prices ORDER BY record_id", conn)  # 读取原始六条价格
info_df = pd.read_sql_query("SELECT * FROM asset_info ORDER BY asset", conn)  # 读取三条正式信息
pandas_left = prices_df.merge(  # 用Pandas连接原表
    info_df, on="asset", how="left", validate="many_to_one",  # 按资产左连接，检查右侧代码唯一
).sort_values("record_id").reset_index(drop=True)  # 使用与SQL相同的排序，并重建默认索引
pandas_inner = prices_df.merge(  # 同样独立实现内连接
    info_df, on="asset", how="inner", validate="many_to_one",  # 只保留两边匹配的组合
).sort_values("record_id").reset_index(drop=True)  # 与SQL的行顺序保持一致
pandas_a = pandas_left.loc[pandas_left["asset"] == target_asset].reset_index(drop=True)  # 从Pandas左连接结果筛A

for result in [left_result, inner_result, sql_a_result, pandas_left, pandas_inner, pandas_a]:  # 遍历待比较表
    result["asset_name"] = result["asset_name"].astype("string")  # 统一文本和缺失值的表示，不填造名称
pd.testing.assert_frame_equal(left_result, pandas_left)  # 对照全部左连接结果
pd.testing.assert_frame_equal(inner_result, pandas_inner)  # 对照全部内连接结果
pd.testing.assert_frame_equal(sql_a_result, pandas_a)  # 对照指定资产的结果
print("正式表的SQL与Pandas三项核对通过。")  # 全部一致才会执行
```


## 8. 在单独演示表中加入重复连接键

正式信息表的asset是主键，不能直接加第二个A。本节另建演示表，只让demo_id唯一，允许asset重复。
演示表有两条A名称映射。价格表每条A记录会匹配两个名称，三个A价格变成六行。
B两条价格各匹配一次，C无匹配仍由LEFT保留，合计3×2+2×1+1=9行。

以下代码用于自己的练习库：

```python
cur.execute("""
CREATE TABLE IF NOT EXISTS asset_info_demo (  -- 单独的重复连接键演示表
    demo_id INTEGER PRIMARY KEY,  -- 行编号唯一；asset本身不设唯一约束
    asset TEXT NOT NULL,  -- 故意允许同一资产出现多条映射
    asset_name TEXT NOT NULL  -- 每条映射的名称
);
""")  # 该表只用于观察重复连接键
demo_rows = [  # 每条演示记录有独立demo_id
    (1, "A", "Asset A"),  # A的第一条映射
    (2, "A", "Asset A alternative"),  # A的第二条映射，故意制造重复连接键
    (3, "B", "Asset B"),  # B一条映射
    (4, "D", "Asset D"),  # D没有价格
]  # 共四条信息
cur.executemany(  # 固定演示主键使本格反复运行不继续增加记录
    "INSERT OR IGNORE INTO asset_info_demo (demo_id, asset, asset_name) VALUES (?, ?, ?)",  # 三个值
    demo_rows,  # 依次绑定演示元组
)  # asset不唯一是本节故意设置，不影响正式信息表
conn.commit()  # 提交演示表写入
sql_demo = """
SELECT p.record_id, p.asset, p.date, p.price, d.asset_name, d.demo_id  -- 多选demo_id辨认不同匹配
FROM prices AS p  -- 六条价格记录
LEFT JOIN asset_info_demo AS d  -- 右表A有两条映射
ON p.asset = d.asset  -- 每条价格匹配右表所有相同资产代码的记录
ORDER BY p.record_id ASC, d.demo_id ASC;  -- 同一价格记录的两条匹配按演示编号排序
"""  # 多行SQL字符串，交给SQLite执行
duplicate_result = pd.read_sql_query(sql_demo, conn)  # 左连接得到重复匹配
print(duplicate_result)  # 预计9行6列，A的每个record_id重复两次
print("重复键连接形状：", duplicate_result.shape)  # 预计(9,6)
assert len(duplicate_result) == 9  # 用行数核对乘法关系
```


## 9. 用Pandas发现并核对重复键

如果业务要求每资产一个名称，merge的many_to_one检查可以及时阻止行数意外膨胀。
下面捕获预期的MergeError作为演示输出，再不加验证重现同样的九行结果。不是把正式信息表改坏。

以下代码用于自己的练习库：

```python
demo_df = pd.read_sql_query("SELECT * FROM asset_info_demo ORDER BY demo_id", conn)  # 读取四条演示映射
duplicate_mask = demo_df.duplicated(subset=["asset"], keep=False)  # 标记所有参与资产代码重复的行
print(demo_df.loc[duplicate_mask])  # 应显示两条A映射
try:  # 本段预计验证失败，演示如何发现重复右键
    prices_df.merge(demo_df, on="asset", how="left", validate="many_to_one")  # 检查右侧键唯一性
except pd.errors.MergeError:  # 捕获Pandas连接关系不符合要求的错误
    print("检测到：右表asset不唯一，不能满足many_to_one。")  # 说明原因，继续下一段演示

pandas_duplicate = prices_df.merge(demo_df, on="asset", how="left")  # 不加验证，观察实际匹配组合
pandas_duplicate = pandas_duplicate.sort_values(["record_id", "demo_id"]).reset_index(drop=True)  # 同SQL排序
pandas_duplicate = pandas_duplicate[["record_id", "asset", "date", "price", "asset_name", "demo_id"]]  # 列顺序一致
duplicate_result["asset_name"] = duplicate_result["asset_name"].astype("string")  # SQL侧统一缺失表示
pandas_duplicate["asset_name"] = pandas_duplicate["asset_name"].astype("string")  # Pandas侧统一缺失表示
pd.testing.assert_frame_equal(duplicate_result, pandas_duplicate)  # 两种方法均应得到相同九行
print("重复键演示：SQL与Pandas结果一致，均为9行。")  # 核对通过
```


## 10. 结束前再重开检查

提交并关闭，重新连接相同文件，仅查询已有表，不再初始化。
价格表六行、正式信息三行、演示信息四行，最后关闭新连接。继续练习时重跑第一格建立连接即可。

以下代码用于自己的练习库：

```python
conn.commit()  # 本次修改全部提交
conn.close()  # 关闭原连接
check_conn = sqlite3.connect(str(db_path))  # 用新的连接打开同一个文件
reopened_price_count = check_conn.execute("SELECT COUNT(*) FROM prices").fetchone()[0]  # 应为6
reopened_info_count = check_conn.execute("SELECT COUNT(*) FROM asset_info").fetchone()[0]  # 应为3
reopened_demo_count = check_conn.execute("SELECT COUNT(*) FROM asset_info_demo").fetchone()[0]  # 应为4
check_conn.close()  # 查询完关闭新连接
print("最终重开核对：", reopened_price_count, reopened_info_count, reopened_demo_count)  # 6、3、4
assert (reopened_price_count, reopened_info_count, reopened_demo_count) == (6, 3, 4)  # 文件数据未丢失
```


## 独立验收

- 自己建立文件库与两张正式表，清楚record_id和asset为何分别作主键。
- 插入后commit、close，再重开同一路径；不重新插入也能查询六条价格。
- 用?参数查询A，解释(target_asset,)的逗号。
- INNER五行、LEFT六行，解释C和D各自的去向。
- 分别读取原表，用Pandas merge实际重做并核对，而不是仅再次读SQL连接结果。
- 手算重复A映射导致3×2+2×1+1=9行，并用SQL/Pandas验证。
- 填写notes.md，保存practice.ipynb和自己的sql_practice.sql。

## 单独运行参考

```powershell
# 参考使用market_reference.sqlite3，不写自己的market_practice.sqlite3。
& "D:\py\Python3\python.exe" "D:\Learning\study\d17\run_sqlite_reference.py"
```

## 常见问题

- no such table：核对db_path是否指向同一个文件；connect只创建库文件，不自动创建价格表。
- Cannot operate on a closed database：连接已关闭，重新connect并建立新游标；不要复用旧cur。
- 数据关闭后不见：检查是否仍用:memory:，是否提交写入，重开路径是否相同。
- UNIQUE constraint failed：普通INSERT重复主键；正式信息表不允许第二个A，重复演示用独立表。
- 改样本后仍旧值：本课INSERT OR IGNORE不更新旧记录；独立重做可换一个新的文件名。
- 参数数量不匹配：?数量对应元组元素数量；单参数写(target_asset,)，不要把?加引号。
- LEFT行数增加：检查右表同一资产是否多条映射，每条左记录会匹配所有右侧同键记录。
- SQL与Pandas名称缺失显示不同：统一astype("string")；不要随意把缺失名称填成某个资产。
- 数据库被其他连接占用：检查另一个Notebook是否有未提交写入，并提交/关闭那一连接后重试。

参考脚本可重复运行，固定样本不会每次多插一份；它不清空已有库、不自动更新你修改的旧主键数据。

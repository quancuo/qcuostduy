# D17 知识点：SQL连接与Python访问SQLite

学习日期：2026-11-03，对应原计划10.27。今天不加算法题，优先完成数据库练习。

## 1. 文件数据库与内存数据库

D16的sqlite3.connect(":memory:")建立临时内存数据库，关闭连接后该库不保留。
今天connect接D盘固定文件路径；文件不存在时创建库文件，但业务表仍需CREATE TABLE创建。
使用绝对路径，避免在不同工作目录下意外创建不同的同名库。
写入后commit提交事务，close关闭连接；再次连接同一文件仍可查询已提交数据。
数据库conn.commit()与Git的git commit是两件事：前者提交数据库事务，后者记录项目文件版本。

## 2. 连接、游标、建表、插入与查询

|写法|接收对象/参数|作用|
|---|---|---|
|sqlite3.connect(str(db_path))|数据库文件路径|返回Connection连接对象，通常命名conn|
|conn.cursor()|当前连接|返回Cursor游标，通常命名cur|
|cur.execute(sql,params)|一条SQL和参数序列|执行一条语句；查询后可取结果|
|cur.executemany(sql,rows)|一条带占位符SQL和多条元组|批量插入本课小样本|
|cur.fetchone()|已执行的查询|返回下一行元组，没有行时为None|
|cur.fetchall()|已执行的查询|返回剩余全部结果组成的列表|
|conn.commit()|有待提交写入的连接|提交事务，保存写入|
|conn.close()|连接对象|关闭连接；旧游标也不再使用|
|pd.read_sql_query(sql,conn,params=...)|查询SQL、连接及可选参数|执行查询并返回DataFrame|

INTEGER是整数，REAL是实数，TEXT是文本；本课日期按YYYY-MM-DD文本存放。
PRIMARY KEY主键标识一条记录。prices的主键为record_id，asset_info的主键为asset。
NOT NULL表示不允许缺失。价格表里同资产多日期记录正常，不应对prices.asset加唯一约束。
CREATE TABLE IF NOT EXISTS不会清空、重建或自动迁移已存在的表结构。
INSERT OR IGNORE只用于本固定样本重复初始化：主键已有则保留旧记录，不会把新值更新进去；它也可能忽略其他适用约束错误，不能当作通用清洗手段。
不需要背完整事务机制；先保证本次写入后commit，再close，再重开查询。

## 3. INNER JOIN与LEFT JOIN

FROM prices AS p LEFT JOIN asset_info AS a ON p.asset=a.asset：p和a是表别名，自定义名字，引用必须一致。
FROM后的prices是本句左表；JOIN后的asset_info是右表。ON是匹配条件，不是Pandas索引对齐。

|方式|含义|本例结果|
|---|---|---|
|INNER JOIN|仅返回能匹配的组合|A三行+B两行=5行，C排除|
|LEFT JOIN|保留左表记录；无匹配时右表字段为NULL|6行，C保留但名称缺失|

右表独有的D没有左侧价格，因此不出现在这两种结果中。
LEFT JOIN和LEFT OUTER JOIN在本课含义相同；今天不要求掌握RIGHT/FULL JOIN。
LEFT JOIN后再用WHERE对右侧字段要求非空或某个值，可能重新筛掉未匹配行；本课指定资产条件使用左侧p.asset。

## 4. 重复连接键为何可能增加行数

SQL会为一条左记录保留所有满足ON的右侧匹配，不会自动选择“第一个名称”。
一条A价格×两个A名称=两行；三条A价格×两个A名称=六行。
重复演示：A贡献3×2=6行；B贡献2×1=2行；C没有匹配但LEFT保留1行；总共9行。
所以“LEFT JOIN行数总等于左表”只在右侧匹配键至多一条等条件下才成立。
正式asset_info.asset为主键，第二个A会被唯一约束拦住。演示表另设demo_id主键，故意允许asset重复。

## 5. 参数绑定

WHERE p.asset = ?中的?占据一个参数值的位置，不加单引号。
cur.execute(sql,(target_asset,))：单元素元组末尾必须有逗号；("A")只是字符串，("A",)才是元组。
不要用f字符串把用户输入值直接拼进SQL。占位符用于数据值，不用于表名、列名等SQL结构。
Pandas读SQL时使用params=(target_asset,)传入同样的参数。

## 6. Pandas对照

SQL INNER JOIN对应merge(how="inner")，LEFT JOIN对应merge(how="left")，ON两侧asset相等对应on="asset"。
validate="many_to_one"表示右侧连接键唯一，左侧可以多条同资产价格；不是要求两边都唯一。
比较前统一列顺序、排序并reset_index。None、NaN可能是SQL/Pandas不同缺失表示，名称列转astype("string")后统一为pd.NA，不要填造不存在的名称。
pd.testing.assert_frame_equal用来核对结果；连接方式一致还应检查记录数、未匹配值和重复键。

## 7. 今天要能解释的新名称

- JOIN：连接两张表；ON：决定哪些行可以匹配。
- PRIMARY KEY：主键；不是说整张表只允许一列数据。
- connection/conn：连接；cursor/cur：游标。
- commit：本课指数据库事务提交，不是Git提交。
- params：parameters的简称，表示查询参数值。
- many_to_one：多对一，左侧多条价格对应右侧一条资产信息。

Python版本仍用本机3.9写法。当前官方教程可能含较新版本接口，本课不使用新版本的autocommit参数。
with conn:通常只管理事务提交/回滚，不会自动关闭连接；本课显式close。

## 查阅

- [廖雪峰：连接查询](https://liaoxuefeng.com/books/sql/query/join/index.html)
- [Python 3.9中文sqlite3](https://docs.python.org/zh-cn/3.9/library/sqlite3.html)
- [SQLite SELECT](https://www.sqlite.org/lang_select.html)
- [SQLite冲突处理与IGNORE](https://www.sqlite.org/lang_conflict.html)
- [Pandas 2.3 merge](https://pandas.pydata.org/pandas-docs/version/2.3/reference/api/pandas.DataFrame.merge.html)

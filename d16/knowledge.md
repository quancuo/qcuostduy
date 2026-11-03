# D16 知识点：SQL查询、过滤、排序、聚合

学习日期：2026-10-31。对应原计划10.26的SQL入门任务，延续为D16。
SQL是Structured Query Language（结构化查询语言），用于表达从数据库中查什么数据。
今天的SELECT只读取结果，不会把源表按结果永久改写。

## 1. 表、行、列与结果

students是学生表；一行是一个学生，列为id、class_id、name、gender、score。
SQL查询结果也是有行和列的结果集；不同SQL工具显示方式不同。
今天在Notebook用pd.read_sql_query(sql, conn)执行SQL并把结果读为Pandas DataFrame。
数据库里的表名students和Python变量students处于不同环境；修改DataFrame不会自动修改数据库表。
id是表里的普通字段名，本例用于学生编号；它不自动变成Pandas的index。

## 2. 核心关键词与Pandas对应

|SQL写法|含义|接什么|Pandas中的近似对应|
|---|---|---|---|
|SELECT id,name|输出哪些列或表达式|列名、表达式、聚合函数|df[["id","name"]]|
|FROM students|从哪里读取|数据库表名|操作的DataFrame|
|WHERE score>=90|过滤原始记录|逐行条件|df.loc[mask]|
|ORDER BY score DESC|决定结果顺序|排序字段与方向|sort_values("score",ascending=False)|
|GROUP BY class_id|按类别组织并聚合|分组字段|groupby("class_id")|
|COUNT(*)|统计记录数|*表示当前组所有行|GroupBy.size()|
|COUNT(score)|统计非NULL成绩数|列名|GroupBy["score"].count()|
|AVG(score)|求非NULL成绩均值|数值列|GroupBy["score"].mean()|
|SUM / MAX / MIN|合计/最大/最小|要汇总的列或表达式|sum / max / min|
|AS average_score|给输出列起别名|新名称|命名聚合的结果列名|

SELECT *中的*表示全部列；COUNT(*)中的*表示按记录计数，不是把全部列的单元格相加。
AVG是average的缩写，DESC是descending降序，ASC是ascending升序。ORDER BY默认升序，但今天显式写ASC便于阅读。
AS只修改当前结果的列名，不会把源表的列改名。别名student_count、average_score是自定义名称，不是SQL保留的特殊字段。

## 3. 书写顺序与理解顺序

常用书写顺序：SELECT → FROM → WHERE → GROUP BY → ORDER BY。每个子句按需出现，不要求每题都有全部部分。
理解本课查询时可按：FROM找表 → WHERE筛行 → GROUP BY/聚合 → SELECT确定输出 → ORDER BY排列结果。
这是帮助理解的逻辑顺序，不是数据库内部必然逐步执行的物理步骤。
WHERE筛的是聚合前的原始行。今天先不展开HAVING、JOIN、窗口函数。
SELECT列名用于选列，WHERE用于选行，不要混淆。

## 4. 语法细节

- SQL相等比较统一写=；Python/Pandas相等比较用==。SQLite也接受==，但本课使用更通用的=。
- SQL字符串用英文单引号，例如gender='F'；列名gender不加单引号。WHERE 'score'>=90不是在正确读取score列。
- SQL组合条件用AND/OR/NOT；Pandas布尔Series用&/|/~，每个比较加括号。混合AND与OR时用括号明确范围。
- SQL逐行注释用--；Python注释用#。在Python的三引号字符串中写SQL时，也用--注释SQL。
- SQL的逗号、引号、括号、分号使用英文半角符号。最后一个SELECT字段后不要多一个逗号。
- 换行和缩进主要用于易读，分号结束语句。Notebook的Python单元格不能直接粘贴裸SELECT；请把SQL放进字符串后调用read_sql_query。
- 本课关键字大写、表名和列名保持样本原样；字符值按实际大小写写M/F。

## 5. 排序和分组易错点

不写ORDER BY时，不应依赖返回顺序；GROUP BY也不保证按分组字段排列。
ORDER BY score DESC,id ASC先按成绩降序，仅在成绩相等时按编号升序。85分的id7排在id10前。
按students.class_id分组只产生1、2、3班三行；classes表虽有4班，但不自动产生零人数的一行。
分组结果中的普通列要来自分组依据，其他列须用恰当聚合。例如按班统计时输出class_id、COUNT(*)、AVG(score)。
不要额外随意输出name；SQLite和网页AlaSQL可能接受这类未分组裸列，但一个姓名无法代表整个班，不能把“能执行”当作正确含义。

## 6. NULL与计数

NULL表示缺失/未知。COUNT(*)数所有记录；COUNT(score)只数非NULL成绩；AVG(score)忽略NULL。
当前十名学生成绩完整，所以两种计数相同；不能由此认为它们永远一样。
例如成绩10、NULL两行：COUNT(*)=2，COUNT(score)=1，AVG(score)=10。
缺失值判断写IS NULL或IS NOT NULL，不写= NULL。今天只需理解，不修改原始样本。
Pandas有一个边界差异：默认sum对全缺失组可能返回0；不要把所有SQL聚合与Pandas默认值当作完全一致。

## 7. 今天的新Python名称

|写法|解释|
|---|---|
|import sqlite3|导入Python自带的数据库接口，无需另装MySQL服务|
|sqlite3.connect(":memory:")|建立临时内存数据库；conn是connection连接对象的常用简称|
|conn.executescript(init_sql)|执行初始化文件中的多条SQL，准备本次查询用的表|
|pd.read_sql_query(sql,conn)|sql接一条查询字符串，conn接连接对象，返回DataFrame|
|三引号字符串|把多行SQL保存为一个Python字符串；它不是注释|
|pd.testing.assert_frame_equal(a,b)|检查两张DataFrame是否一致，失败时说明差异|
|conn.close()|关闭连接；若关闭本课内存库，继续查询前需重新初始化|

本地初始化SQL属于环境准备。今天优先掌握SELECT、WHERE、ORDER BY和GROUP BY，不要求背建表/插入语句。

## 查阅

- [网页在线练习](https://liaoxuefeng.com/books/sql/sql-online/index.html)
- [廖雪峰：查询数据与样本来源](https://liaoxuefeng.com/books/sql/query/index.html)
- [廖雪峰：聚合查询](https://liaoxuefeng.com/books/sql/query/aggregation/index.html)
- [SQLite SELECT官方说明](https://www.sqlite.org/lang_select.html)
- [SQLite聚合官方说明](https://www.sqlite.org/lang_aggfunc.html)
- [Python 3.9 sqlite3](https://docs.python.org/3.9/library/sqlite3.html)
- [Pandas 2.3 read_sql_query](https://pandas.pydata.org/pandas-docs/version/2.3/reference/api/pandas.read_sql_query.html)

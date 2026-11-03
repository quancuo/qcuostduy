# D16 实操：SQL查询、过滤、排序、聚合

学习日期：2026-10-31，对应原计划10.26的任务。先在网页完成五条查询，再在本机验证，并用Pandas重做其中两题。
目标：能解释SELECT、WHERE、ORDER BY、GROUP BY各自负责什么；能自己选择列、组合条件、降序排序、按类别计数求平均。

## 建议节奏

- 中文课程60～75分钟：基本查询、条件查询、投影查询、排序、聚合查询。
- 网页五题30～40分钟：先预测结果，每次只运行一条SELECT。
- 本地复现与两道Pandas对照45～60分钟。
- 关闭参考独立复写、手算平均分与笔记20～30分钟。

## 第一步：先网页练习

打开[在线SQL](https://liaoxuefeng.com/books/sql/sql-online/index.html)或对应章节的可编辑SQL示例。
网页已准备students和classes表。将一条SELECT填入执行框并运行，观察结果；刷新页面会恢复初始数据。
今天先不修改样本。把自己写的五条查询保存到web_practice.sql；VS Code用于编辑保存，网页负责执行SQL。
如果网页执行框未加载，可用后面的本机Notebook练习同题；网页和本地的运行结果请分开记录。

| 字段 | 含义 |
|---|---|
|id|学生编号，1到10|
|class_id|班级编号，学生分布于1、2、3班|
|name|姓名|
|gender|网页样本的性别标记，M/F|
|score|成绩，当前十条数据均非空|

classes中还有四班，但students里没有四班学生，今天只对students分组时不会产生四班结果。
数据来自[教程准备数据页](https://liaoxuefeng.com/books/sql/query/index.html)，本机初始化文件复现同一组小样本。

## 五道网页题：先自己写，再看单独答案


### q1 选择指定列

只显示id、name、score，并按id升序。先预测10行3列。

预计：10行3列；id从1到10。


### q2 两个条件筛选并排序

查询女生且成绩至少90分，只输出id、name、score；按分数降序，同分按id升序。

预计：2行3列：(2,小红,95)、(8,小新,91)。


### q3 全部成绩降序

不做筛选，显示id、name、score；所有成绩降序，同分编号升序。

预计：10行3列；编号顺序2、8、1、9、3、7、10、5、4、6。


### q4 按类别计数

以class_id作为类别，统计每个班级人数，按班级编号升序。

预计：3行2列：1班4人、2班3人、3班3人。


### q5 按类别计数并求平均

每班输出班级编号、人数、平均分，并手算一班平均分核对。

预计：3行3列；人数4/3/3，平均分86.5、73.6666667、88.3333333。


答案保存在queries_reference.sql，每行都有中文注释。网页题写完后再打开对照，不必一次复制整份文件。

## 第二步：打开本机Notebook

```powershell
# &是PowerShell调用运算符，运行已有的D盘Jupyter启动器。
& "D:\Learning\Start-Jupyter.cmd"
```

Jupyter已经打开时，刷新文件列表进入d16，打开practice.ipynb。内核选择Python (D Learning)。
Shift+Enter运行，Ctrl+S保存。初始化格已经提供，其余格留给你填写；逐行答案在reference.ipynb。
本机使用Python自带sqlite3。临时数据库只在内存中；重启内核后重新运行初始化格即可。

| 文件 | 用途 |
|---|---|
|knowledge.md|知识点与SQL/Pandas对应表|
|web_practice.sql|保存自己写的网页查询|
|queries_reference.sql|五题SQL逐行参考|
|practice.ipynb|本机练习，初始化格已准备|
|reference.ipynb|分节、逐行中文注释参考|
|data/init_students.sql|复现网页学生与班级样本|
|run_sql_reference.py|可直接运行的本机参考脚本|
|outputs/query_results.txt|脚本运行得到的五题参考结果|
|notes.md / notes_reference.md|问答题与分开的答案|

## 第三步：本机逐步操作


### 1. 本机初始化：准备十名学生

先完成网页的五题，再在本机核对同一批数据。网页使用AlaSQL，本机使用SQLite；今天这五条基础SELECT可在两者运行。
本机只需已有Python和Pandas。每次运行本格都建立一个新的临时内存数据库，不生成数据库文件。
数据库表和Python变量不是同一对象：FROM students引用数据库表；Python中的students是查询得到的DataFrame。
若重启内核，内存数据库会消失；重新运行本格即可恢复样本。

```python
import sqlite3  # Python自带的SQLite接口；SQLite是轻量数据库引擎
import pandas as pd  # pandas用于显示结果和完成后面的对照题
from pathlib import Path  # Path用于拼接文件路径

base_dir = Path("D:/Learning/study/d16")  # 今天的D16文件夹
conn = sqlite3.connect(":memory:")  # conn是connection连接对象；:memory:表示临时内存数据库
init_sql = (base_dir / "data" / "init_students.sql").read_text(encoding="utf-8")  # 读取已准备好的初始化SQL
conn.executescript(init_sql)  # 一次执行建表和填入样本的多条语句；这一步今天可先直接使用

students = pd.read_sql_query("SELECT * FROM students ORDER BY id ASC;", conn)  # 在数据库查询全部列，结果转成DataFrame
print(students)  # 核对十名学生；最左侧0到9是Pandas索引，id列的1到10是学生编号
print(students.shape)  # 预计(10, 5)
```


### 2. SQL：选择指定列

只显示id、name、score，并按id升序。先预测10行3列。

预期：10行3列；id从1到10。

```python
q1_sql = """
SELECT id, name, score  -- SELECT后写需要输出的列，用英文逗号分开
FROM students  -- FROM后是数据库里的表名
ORDER BY id ASC;  -- 按编号升序；分号结束这条语句
"""  # 三个双引号将多行SQL保存为Python字符串
q1 = pd.read_sql_query(q1_sql, conn)  # 执行这一条查询，并把结果读为DataFrame
print(q1)  # 核对查询结果
print(q1.shape)  # 10行3列；id从1到10。
```


### 3. SQL：两个条件筛选并排序

查询女生且成绩至少90分，只输出id、name、score；按分数降序，同分按id升序。

预期：2行3列：(2,小红,95)、(8,小新,91)。

```python
q2_sql = """
SELECT id, name, score  -- 结果只显示三个字段
FROM students  -- 从学生表读取记录
WHERE gender = 'F' AND score >= 90  -- 两个条件同时成立；字符串用英文单引号
ORDER BY score DESC, id ASC;  -- 分数从高到低，同分按编号从小到大
"""  # 三个双引号将多行SQL保存为Python字符串
q2 = pd.read_sql_query(q2_sql, conn)  # 执行这一条查询，并把结果读为DataFrame
print(q2)  # 核对查询结果
print(q2.shape)  # 2行3列：(2,小红,95)、(8,小新,91)。
```


### 4. SQL：全部成绩降序

不做筛选，显示id、name、score；所有成绩降序，同分编号升序。

预期：10行3列；编号顺序2、8、1、9、3、7、10、5、4、6。

```python
q3_sql = """
SELECT id, name, score  -- 选择结果列
FROM students  -- 读取所有学生
ORDER BY score DESC, id ASC;  -- 降序优先；第二个键只决定同分者的顺序
"""  # 三个双引号将多行SQL保存为Python字符串
q3 = pd.read_sql_query(q3_sql, conn)  # 执行这一条查询，并把结果读为DataFrame
print(q3)  # 核对查询结果
print(q3.shape)  # 10行3列；编号顺序2、8、1、9、3、7、10、5、4、6。
```


### 5. SQL：按类别计数

以class_id作为类别，统计每个班级人数，按班级编号升序。

预期：3行2列：1班4人、2班3人、3班3人。

```python
q4_sql = """
SELECT class_id, COUNT(*) AS student_count  -- 输出班级和人数；AS给结果列起别名
FROM students  -- 统计学生记录
GROUP BY class_id  -- 相同班级编号归为一组，每组统计一次
ORDER BY class_id ASC;  -- 明确按班级编号排序，GROUP BY不代替ORDER BY
"""  # 三个双引号将多行SQL保存为Python字符串
q4 = pd.read_sql_query(q4_sql, conn)  # 执行这一条查询，并把结果读为DataFrame
print(q4)  # 核对查询结果
print(q4.shape)  # 3行2列：1班4人、2班3人、3班3人。
```


### 6. SQL：按类别计数并求平均

每班输出班级编号、人数、平均分，并手算一班平均分核对。

预期：3行3列；人数4/3/3，平均分86.5、73.6666667、88.3333333。

```python
q5_sql = """
SELECT class_id,  -- 分组依据也放入结果，方便辨认各组
       COUNT(*) AS student_count,  -- 统计各组记录数，不要求成绩非空
       AVG(score) AS average_score  -- AVG是average，计算各组非空成绩平均值
FROM students  -- 数据来源为学生表
GROUP BY class_id  -- 按班级聚合
ORDER BY class_id ASC;  -- 结果按班级编号升序
"""  # 三个双引号将多行SQL保存为Python字符串
q5 = pd.read_sql_query(q5_sql, conn)  # 执行这一条查询，并把结果读为DataFrame
print(q5)  # 核对查询结果
print(q5.shape)  # 3行3列；人数4/3/3，平均分86.5、73.6666667、88.3333333。
```


### 7. Pandas对照一：筛选、选列与排序

先关闭SQL参考，用Pandas独立重做q2。它必须实际用loc和sort_values，而不是再次执行SQL来冒充Pandas实现。

```python
mask = (students["gender"] == "F") & (students["score"] >= 90)  # Pandas逐行布尔条件，用==和&，各比较加括号
pandas_q2 = students.loc[mask, ["id", "name", "score"]]  # 先筛行，再只保留需要的三列
pandas_q2 = pandas_q2.sort_values(  # 返回排序结果，要重新赋给变量
    ["score", "id"],  # 两个排序键：先分数，再编号
    ascending=[False, True],  # False对应DESC降序，True对应ASC升序
).reset_index(drop=True)  # 重建默认索引，便于与SQL结果逐行比较

print(pandas_q2)  # 应与前面SQL q2相同：小红95、小新91
pd.testing.assert_frame_equal(pandas_q2, q2)  # 检查两张表的列、行、数值与索引相同
```


### 8. Pandas对照二：分组计数与平均

独立重做q5。COUNT(*)对应size，AVG(score)对应mean；reset_index将分组索引恢复成普通列。

```python
pandas_q5 = students.groupby("class_id").agg(  # 相同班级归一组；此处是groupby，没有subset参数
    student_count=("id", "size"),  # 对应SQL COUNT(*)，统计组内行数
    average_score=("score", "mean"),  # 对应SQL AVG(score)，对非空成绩求平均
).reset_index()  # 把班级索引恢复为普通列，与SQL结果列结构相同
pandas_q5 = pandas_q5.sort_values("class_id").reset_index(drop=True)  # 明确排序，重建默认索引

print(pandas_q5)  # 预计三行三列，各班人数4、3、3
pd.testing.assert_frame_equal(  # 比较SQL和Pandas分组结果
    pandas_q5, q5,  # 两个待比较DataFrame
    check_exact=False, rtol=1e-12, atol=1e-12,  # 平均分允许极小浮点误差
)
print("两道SQL与Pandas对照均通过。")  # 所有比较通过后才会输出
```


## 第四步：手算与独立验收

一班四人成绩90、95、88、73，总分346，平均346/4=86.5。
二班总分221，人数3，平均73.6666667；三班总分265，人数3，平均88.3333333。
平均分显示小数位可能不同，比较实际数值，允许极小浮点误差。

- 能从空白写SELECT选列、WHERE组合条件、ORDER BY降序与同分次序。
- 能按班级COUNT(*)和AVG(score)，解释分组结果为什么三行。
- 独立用Pandas重做筛选排序题和分组汇总题，两份结果与SQL一致。
- 能解释SQL的=、AND与Pandas的==、&的差异，以及COUNT(*)与COUNT(score)的区别。
- 填写notes.md并保存自己的practice.ipynb、web_practice.sql。

## 参考脚本运行方式

```powershell
# 使用D盘Python执行完整本机参考，输出五题结果并核对Pandas对照。
& "D:\py\Python3\python.exe" "D:\Learning\study\d16\run_sql_reference.py"
```

## 常见报错

- Python提示SyntaxError且指向SELECT：把SQL写进三引号字符串，再调用pd.read_sql_query，不直接运行裸SQL。
- no such table或conn未定义：回到初始化格，从上往下运行；网页和本机不共享连接或数据库。
- near WHERE语法错误：检查子句顺序、末列多余逗号、是否使用中文标点。
- no such column：核对列名拼写；字符串F需要写为'F'。
- 结果行数意外变多：检查AND是否误写OR，以及条件括号范围。
- 结果看起来顺序不一致：显式添加ORDER BY，Pandas也用相同排序键并reset_index。
- 分组多出姓名但本机仍能运行：不要借助SQLite/AlaSQL对裸列的宽松行为；按班汇总只输出班级与聚合值。

"""D16参考脚本：五条SQL与两个Pandas对照题。"""


def main():  # 按顺序运行查询和对照
    # 1. 本机初始化：准备十名学生
    import sqlite3  # Python自带的SQLite接口；SQLite是轻量数据库引擎
    import pandas as pd  # pandas用于显示结果和完成后面的对照题
    from pathlib import Path  # Path用于拼接文件路径

    base_dir = Path(__file__).resolve().parent  # 今天的D16文件夹
    conn = sqlite3.connect(":memory:")  # conn是connection连接对象；:memory:表示临时内存数据库
    init_sql = (base_dir / "data" / "init_students.sql").read_text(encoding="utf-8")  # 读取已准备好的初始化SQL
    conn.executescript(init_sql)  # 一次执行建表和填入样本的多条语句；这一步今天可先直接使用

    students = pd.read_sql_query("SELECT * FROM students ORDER BY id ASC;", conn)  # 在数据库查询全部列，结果转成DataFrame
    print(students)  # 核对十名学生；最左侧0到9是Pandas索引，id列的1到10是学生编号
    print(students.shape)  # 预计(10, 5)


    # 2. SQL：选择指定列
    q1_sql = """
    SELECT id, name, score  -- SELECT后写需要输出的列，用英文逗号分开
    FROM students  -- FROM后是数据库里的表名
    ORDER BY id ASC;  -- 按编号升序；分号结束这条语句
    """  # 三个双引号将多行SQL保存为Python字符串
    q1 = pd.read_sql_query(q1_sql, conn)  # 执行这一条查询，并把结果读为DataFrame
    print(q1)  # 核对查询结果
    print(q1.shape)  # 10行3列；id从1到10。


    # 3. SQL：两个条件筛选并排序
    q2_sql = """
    SELECT id, name, score  -- 结果只显示三个字段
    FROM students  -- 从学生表读取记录
    WHERE gender = 'F' AND score >= 90  -- 两个条件同时成立；字符串用英文单引号
    ORDER BY score DESC, id ASC;  -- 分数从高到低，同分按编号从小到大
    """  # 三个双引号将多行SQL保存为Python字符串
    q2 = pd.read_sql_query(q2_sql, conn)  # 执行这一条查询，并把结果读为DataFrame
    print(q2)  # 核对查询结果
    print(q2.shape)  # 2行3列：(2,小红,95)、(8,小新,91)。


    # 4. SQL：全部成绩降序
    q3_sql = """
    SELECT id, name, score  -- 选择结果列
    FROM students  -- 读取所有学生
    ORDER BY score DESC, id ASC;  -- 降序优先；第二个键只决定同分者的顺序
    """  # 三个双引号将多行SQL保存为Python字符串
    q3 = pd.read_sql_query(q3_sql, conn)  # 执行这一条查询，并把结果读为DataFrame
    print(q3)  # 核对查询结果
    print(q3.shape)  # 10行3列；编号顺序2、8、1、9、3、7、10、5、4、6。


    # 5. SQL：按类别计数
    q4_sql = """
    SELECT class_id, COUNT(*) AS student_count  -- 输出班级和人数；AS给结果列起别名
    FROM students  -- 统计学生记录
    GROUP BY class_id  -- 相同班级编号归为一组，每组统计一次
    ORDER BY class_id ASC;  -- 明确按班级编号排序，GROUP BY不代替ORDER BY
    """  # 三个双引号将多行SQL保存为Python字符串
    q4 = pd.read_sql_query(q4_sql, conn)  # 执行这一条查询，并把结果读为DataFrame
    print(q4)  # 核对查询结果
    print(q4.shape)  # 3行2列：1班4人、2班3人、3班3人。


    # 6. SQL：按类别计数并求平均
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


    # 7. Pandas对照一：筛选、选列与排序
    mask = (students["gender"] == "F") & (students["score"] >= 90)  # Pandas逐行布尔条件，用==和&，各比较加括号
    pandas_q2 = students.loc[mask, ["id", "name", "score"]]  # 先筛行，再只保留需要的三列
    pandas_q2 = pandas_q2.sort_values(  # 返回排序结果，要重新赋给变量
        ["score", "id"],  # 两个排序键：先分数，再编号
        ascending=[False, True],  # False对应DESC降序，True对应ASC升序
    ).reset_index(drop=True)  # 重建默认索引，便于与SQL结果逐行比较

    print(pandas_q2)  # 应与前面SQL q2相同：小红95、小新91
    pd.testing.assert_frame_equal(pandas_q2, q2)  # 检查两张表的列、行、数值与索引相同


    # 8. Pandas对照二：分组计数与平均
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

    output_dir = base_dir / "outputs"  # 查询结果保存位置
    output_dir.mkdir(parents=True, exist_ok=True)  # 创建输出目录
    parts = []  # 收集五题输出文字
    for label, result in [("q1",q1),("q2",q2),("q3",q3),("q4",q4),("q5",q5)]:  # 依次取结果
        parts.append(label + "\n" + result.to_string(index=False))  # 只显示字段，不额外显示Pandas索引
    (output_dir / "query_results.txt").write_text("\n\n".join(parts), encoding="utf-8")  # 保存参考查询结果
    conn.close()  # 脚本完成后关闭临时数据库连接


if __name__ == "__main__":  # 直接执行才运行，导入时不初始化数据库
    main()  # 开始本机参考练习

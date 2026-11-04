"""D17参考：SQLite文件库持久化、参数查询、JOIN与Pandas核对。"""


def main():  # 按顺序执行本机参考流程
    # 1. 连接D盘文件数据库
    import sqlite3  # Python自带SQLite接口，不需要再安装数据库服务器
    import pandas as pd  # 用于展示SQL结果并完成merge对照
    from pathlib import Path  # 用于表示和连接文件路径

    base_dir = Path(__file__).resolve().parent  # 今天的练习目录
    data_dir = base_dir / "data"  # 数据库文件存放目录
    data_dir.mkdir(parents=True, exist_ok=True)  # 父文件夹缺少时一起创建，已存在时不报错
    db_path = data_dir / "market_reference.sqlite3"  # 参考专用文件；自己的练习改为market_practice.sqlite3
    conn = sqlite3.connect(str(db_path))  # 连接文件数据库；不存在时创建文件，不会自动创建业务表
    cur = conn.cursor()  # 创建游标，用于执行下面的SQL
    print(db_path)  # 确认数据库实际保存在D盘


    # 2. 创建价格表和正式资产信息表
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


    # 3. 批量插入小样本并提交
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


    # 4. 关闭后重开，先验证持久化
    conn.close()  # 关闭当前连接，前一格已经提交写入
    conn = sqlite3.connect(str(db_path))  # 重开同一文件；这里没有重新插入数据
    cur = conn.cursor()  # 为新连接创建新游标
    price_count = cur.execute("SELECT COUNT(*) FROM prices").fetchone()[0]  # 重开后仍应有6条价格
    info_count = cur.execute("SELECT COUNT(*) FROM asset_info").fetchone()[0]  # 正式信息仍应有3条
    print("重开后价格条数：", price_count, "信息条数：", info_count)  # 预计6和3
    assert price_count == 6 and info_count == 3  # 核对数据确实保存在文件中


    # 5. 参数查询指定资产，并连接名称
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


    # 6. 对比INNER JOIN和LEFT JOIN
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


    # 7. 用Pandas merge真正重做并核对
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


    # 8. 在单独演示表中加入重复连接键
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


    # 9. 用Pandas发现并核对重复键
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


    # 10. 结束前再重开检查
    conn.commit()  # 本次修改全部提交
    conn.close()  # 关闭原连接
    check_conn = sqlite3.connect(str(db_path))  # 用新的连接打开同一个文件
    reopened_price_count = check_conn.execute("SELECT COUNT(*) FROM prices").fetchone()[0]  # 应为6
    reopened_info_count = check_conn.execute("SELECT COUNT(*) FROM asset_info").fetchone()[0]  # 应为3
    reopened_demo_count = check_conn.execute("SELECT COUNT(*) FROM asset_info_demo").fetchone()[0]  # 应为4
    check_conn.close()  # 查询完关闭新连接
    print("最终重开核对：", reopened_price_count, reopened_info_count, reopened_demo_count)  # 6、3、4
    assert (reopened_price_count, reopened_info_count, reopened_demo_count) == (6, 3, 4)  # 文件数据未丢失

    output_dir = base_dir / "outputs"  # 参考结果目录
    output_dir.mkdir(parents=True, exist_ok=True)  # 创建结果目录
    parts = []  # 收集需要对照的查询结果
    for label, result in [("A",sql_a_result),("INNER",inner_result),("LEFT",left_result),("DUPLICATE",duplicate_result)]:  # 依次展示四类结果
        parts.append(label + "\n" + result.to_string(index=False))  # 保存字段与记录，不额外显示Pandas索引
    (output_dir / "join_results.txt").write_text("\n\n".join(parts), encoding="utf-8")  # 另存可读参考结果


if __name__ == "__main__":  # 直接运行才执行，导入不自动建库
    main()  # 开始参考流程

CREATE TABLE IF NOT EXISTS prices (  -- 表不存在才创建，重复运行不删除已有表
    record_id INTEGER PRIMARY KEY,  -- 每条价格记录的唯一编号
    asset TEXT NOT NULL,  -- 资产代码，允许同一资产有多个日期的价格
    date TEXT NOT NULL,  -- 本课用YYYY-MM-DD格式文本保存日期
    price REAL NOT NULL  -- REAL表示实数；本课小样本价格
);

CREATE TABLE IF NOT EXISTS asset_info (  -- 正式资产信息表
    asset TEXT PRIMARY KEY NOT NULL,  -- 每个资产代码只允许一条信息，不允许空代码
    asset_name TEXT NOT NULL  -- 资产名称
);

CREATE TABLE IF NOT EXISTS asset_info_demo (  -- 单独的重复连接键演示表
    demo_id INTEGER PRIMARY KEY,  -- 行编号唯一；asset本身不设唯一约束
    asset TEXT NOT NULL,  -- 故意允许同一资产出现多条映射
    asset_name TEXT NOT NULL  -- 每条映射的名称
);

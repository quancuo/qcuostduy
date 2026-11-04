-- 在Notebook或Python连接中运行；含?的查询须同时传入参数。

-- 指定资产
SELECT p.record_id, p.asset, p.date, p.price, a.asset_name  -- 选择价格字段和右表名称
FROM prices AS p  -- p是价格表的自定义别名
LEFT JOIN asset_info AS a  -- a是资产信息表别名，保留左侧价格记录
ON p.asset = a.asset  -- 按资产代码匹配，不按行号匹配
WHERE p.asset = ?  -- ?是参数值占位符，不加引号
ORDER BY p.date ASC, p.record_id ASC;  -- 明确按日期、记录编号排序

-- INNER JOIN
SELECT p.record_id, p.asset, p.date, p.price, a.asset_name  -- 从两表选取需要的字段
FROM prices AS p  -- 左表为价格表
INNER JOIN asset_info AS a  -- 仅保留按ON条件能匹配的组合
ON p.asset = a.asset  -- 资产代码相同才匹配
ORDER BY p.record_id ASC;  -- 按记录编号展示

-- LEFT JOIN
SELECT p.record_id, p.asset, p.date, p.price, a.asset_name  -- 输出五列
FROM prices AS p  -- 左表是价格记录
LEFT JOIN asset_info AS a  -- 保留所有左表记录；右表没有匹配时补NULL
ON p.asset = a.asset  -- 连接条件
ORDER BY p.record_id ASC;  -- 明确结果顺序

-- 重复连接键
SELECT p.record_id, p.asset, p.date, p.price, d.asset_name, d.demo_id  -- 多选demo_id辨认不同匹配
FROM prices AS p  -- 六条价格记录
LEFT JOIN asset_info_demo AS d  -- 右表A有两条映射
ON p.asset = d.asset  -- 每条价格匹配右表所有相同资产代码的记录
ORDER BY p.record_id ASC, d.demo_id ASC;  -- 同一价格记录的两条匹配按演示编号排序


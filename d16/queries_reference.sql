-- D16查询参考：每次复制一条SELECT到网页运行，先预测结果再执行。

-- q1 选择指定列：10行3列；id从1到10。
SELECT id, name, score  -- SELECT后写需要输出的列，用英文逗号分开
FROM students  -- FROM后是数据库里的表名
ORDER BY id ASC;  -- 按编号升序；分号结束这条语句

-- q2 两个条件筛选并排序：2行3列：(2,小红,95)、(8,小新,91)。
SELECT id, name, score  -- 结果只显示三个字段
FROM students  -- 从学生表读取记录
WHERE gender = 'F' AND score >= 90  -- 两个条件同时成立；字符串用英文单引号
ORDER BY score DESC, id ASC;  -- 分数从高到低，同分按编号从小到大

-- q3 全部成绩降序：10行3列；编号顺序2、8、1、9、3、7、10、5、4、6。
SELECT id, name, score  -- 选择结果列
FROM students  -- 读取所有学生
ORDER BY score DESC, id ASC;  -- 降序优先；第二个键只决定同分者的顺序

-- q4 按类别计数：3行2列：1班4人、2班3人、3班3人。
SELECT class_id, COUNT(*) AS student_count  -- 输出班级和人数；AS给结果列起别名
FROM students  -- 统计学生记录
GROUP BY class_id  -- 相同班级编号归为一组，每组统计一次
ORDER BY class_id ASC;  -- 明确按班级编号排序，GROUP BY不代替ORDER BY

-- q5 按类别计数并求平均：3行3列；人数4/3/3，平均分86.5、73.6666667、88.3333333。
SELECT class_id,  -- 分组依据也放入结果，方便辨认各组
       COUNT(*) AS student_count,  -- 统计各组记录数，不要求成绩非空
       AVG(score) AS average_score  -- AVG是average，计算各组非空成绩平均值
FROM students  -- 数据来源为学生表
GROUP BY class_id  -- 按班级聚合
ORDER BY class_id ASC;  -- 结果按班级编号升序

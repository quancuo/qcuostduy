-- D16网页练习数据的本地复现。来源：https://liaoxuefeng.com/books/sql/query/index.html
-- 此脚本用于新建的SQLite内存数据库；今天先理解查询，不要求掌握建表和插入语法。
CREATE TABLE students (  -- 学生表，每行表示一个学生
    id INTEGER PRIMARY KEY,  -- 学生编号；不是Pandas默认行索引
    class_id INTEGER NOT NULL,  -- 班级编号
    name TEXT NOT NULL,  -- 姓名
    gender TEXT NOT NULL,  -- 网页样本用M/F标记性别
    score INTEGER  -- 成绩；当前十条样本均非空
);
INSERT INTO students (id, class_id, name, gender, score) VALUES
    (1, 1, '小明', 'M', 90),
    (2, 1, '小红', 'F', 95),
    (3, 1, '小军', 'M', 88),
    (4, 1, '小米', 'F', 73),
    (5, 2, '小白', 'F', 81),
    (6, 2, '小兵', 'M', 55),
    (7, 2, '小林', 'M', 85),
    (8, 3, '小新', 'F', 91),
    (9, 3, '小王', 'M', 89),
    (10, 3, '小丽', 'F', 85);
CREATE TABLE classes (  -- 班级表，今天只观察，不进行连接查询
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
INSERT INTO classes (id, name) VALUES
    (1, '一班'), (2, '二班'), (3, '三班'), (4, '四班');

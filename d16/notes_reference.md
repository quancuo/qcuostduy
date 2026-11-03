# D16 问答参考

## 1. SELECT、FROM、WHERE、ORDER BY、GROUP BY分别负责什么？

SELECT定输出列/表达式，FROM指定来源表，WHERE筛原始行，GROUP BY按类别聚合，ORDER BY规定结果顺序。

## 2. SELECT name,score与WHERE score>=90的区别？

前者选列，后者选行；可以在同一条查询中组合。

## 3. SQL的=和AND与Pandas的写法有什么不同？

SQL用=比较相等，用AND组合条件；Pandas用==，逐行布尔Series用&且各比较加括号。SQLite虽然也接受==，本课统一写=。

## 4. DESC与ASC是什么？同分的稳定次序怎样明确？

DESC降序、ASC升序；ORDER BY score DESC,id ASC表示同分时id小的在前，不写第二排序键就不能依赖同分顺序。

## 5. COUNT(*)、COUNT(score)、AVG(score)遇到NULL时怎样处理？

COUNT(*)统计所有行，COUNT(score)只计非NULL项，AVG(score)按非NULL成绩求平均；当前完整样本两种计数相同。

## 6. AS会改掉原表列名吗？

不会，只给这次查询输出列起别名，如student_count。

## 7. 分组后为什么只有三行？为什么没有四班？

students中只有1/2/3三种class_id；只查询该表不会自动引入classes里的四班。

## 8. 一班人数和平均分怎样手算？

人数4；总分90+95+88+73=346；平均346/4=86.5。

## 9. 按class_id分组时可以随意在SELECT里加name吗？

不应随意加。name不是分组依据，也没有聚合，一个姓名不代表整班。SQLite/AlaSQL可能接受这种裸列，但语义仍不合理。

## 10. GROUP BY能替代ORDER BY吗？

不能；前者组织聚合，后者控制最终顺序。需要班级编号升序时显式ORDER BY class_id ASC。

## 11. 网页students表和Python变量students是一个对象吗？

不是。网页、本地数据库及Python变量各有环境；Python students是本地查询得到的DataFrame，不自动修改数据库表。

## 12. 重启内核后no such table或conn未定义怎样处理？

重新从本地初始化格开始运行；内存数据库不跨内核保存。不要在Python单元格直接运行裸SELECT。

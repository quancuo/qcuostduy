# D11 问答：分组与聚合

学习日期：2026-10-25。先独立回答，再打开 notes_reference.md 核对。

1. 今天 data/prices.csv 来源于哪份样本？改了哪个记录的什么内容？为什么不直接用 D10 清洗后的七行？
2. groupby("asset") 根据什么分组？执行后是否已经生成了两行汇总表？原表 df 还有几行？
3. grouped、summary、record_count 哪些是我们自己的名字？asset、price、size、count 又分别起什么作用？
4. 为什么 A 的 size 为 4，price 的 count 为 3？价格缺失的那一行是否属于 A 组？
5. df.size、df.shape[0]、df.groupby("asset").size() 各表示什么？对今天的八行五列原表分别是多少？
6. count 会不会自动排除空字符串或 not-a-number？为什么先转换数值后，才能在本例中把它称为有效价格数？0 会不会被 count 排除？
7. 请逐部分解释 valid_price_count=("price", "count")；为什么 record_count=("price", "size") 仍会计入空价格行？
8. as_index=False 的作用是什么？当前 summary 为什么是两行七列？如果按 asset 和 date 两列一起分组，还会只有两组吗？
9. A 的六项手算结果分别是什么？价格缺失的 10 月 14 日那条记录是否计入日期范围？计算起止日期为什么使用 min/max？
10. 为什么不把缺失价格填成 0？如果一组所有价格都缺失，count、min、max 会有什么结果？
11. index=False 会不会让 asset 列在 CSV 中丢失？CSV 能否保存 date 列的 Pandas 日期类型？
12. 汇总后的 record_count 合计与 valid_price_count 合计分别是多少？两者相差多少，它对应哪条记录？

## 我的回答

在这里逐题写下自己的解释。

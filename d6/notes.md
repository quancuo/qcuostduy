我要取：第 2 天的全部主题
预计结果：
预计 shape：

| 任务 | 我的表达式 | 预计 shape | 实际 shape |
|---|---|---|---|
| 取第 5 天的全部主题 |  |  |  |
result = minutes[4, :]

print(result)
print("实际 shape =", result.shape)
| 取前 3 天的全部主题 |  |  |  |
result = minutes[0:3, :]

print(result)
print("实际 shape =", result.shape)
| 取 Git 主题，保留二维的一列 |  |  |  |
result = minutes[:, 1:2]

print(result)
print("实际 shape =", result.shape)
| 取第 4～5 天的 Git 和数学 |  |  |  |
result = minutes[3:5, 1:3]----------3,4 , 1,2

print(result)
print("实际 shape =", result.shape)
| 筛选大于等于 30 分钟的元素 |  |  |  |
over30 = minutes >= 30
print = [over30]
| 将原数组变成 1 行、15 列 |  |  |  |
minutes.reshaped(1,15)

1. 原数组的两个维度分别表示什么？
2. shape、ndim、size 分别是什么？
3. 为什么取一天得到 (3,)，而不是 (1, 3)？
4. 冒号 : 表示什么？切片终点是否包含？
单独的 :：选取这一维的全部数据。
开始:结束：选取指定范围，包含开始，不包含结束。
5. 为什么布尔标记是 (5, 3)，筛选结果却是 (7,)？
6. reshape(3, 5) 与转置为什么排列不同？
reshape(3, 5) 默认按原来的行顺序读取 15 个数，再每 5 个数分成一行：

7. 基本切片得到的视图，与 copy() 得到的副本有什么区别？
视图 view 是另一个数组对象，但与原数组共享底层数据：
view = minutes[:, 0]
修改 view[0]，原数组中的 minutes[0, 0] 也会变化。

副本 copy 对今天这种普通数字数组拥有独立的数据：
copied = minutes[:, 0].copy()
修改 copied[0]，原数组保持原来的值。
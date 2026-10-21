# D9 问答：索引、筛选、排序与集合

日期：2026-10-20。请先独立作答，再运行代码核对。

1. index 索引标签与行位置有什么区别？设置 record_id 索引后，shape 为什么从 (8, 5) 变成 (8, 4)？
2. df["asset"] == "A" 得到什么类型和多少个判断结果？它会直接返回筛选后的表吗？
3. = 与 == 分别表示什么？为什么今天组合条件用 & 而不是 and？
4. 为什么 (df["asset"] == "A") & (df["price"] > 103) 中每个比较条件都要加括号？
5. > 103 与 >= 103 有什么区别？筛选结果为 (0, 4) 是否一定是报错？
6. sample(frac=1, random_state=42) 中两个参数分别有什么作用？
7. sort_values(["asset", "date"]) 的第一、第二排序依据分别是什么？日期是全表统一升序吗？
8. 排序后索引为什么没有自动变成 0～7？ordered.iloc[1] 与 ordered.loc[102] 分别选哪条记录？
9. sort_values、sort_index、reset_index 分别做什么？reset_index(drop=True) 会怎样处理旧标签？
10. set() 与 {} 分别创建什么？集合的 add 与列表的 append 分别用于什么容器？
11. 217 为什么必须先检查 number in seen，再 seen.add(number)？
12. 217 的 return False 为什么不能放在循环的第一轮末尾？用 [2, 5, 2] 解释。

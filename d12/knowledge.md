# D12 知识点：合并与独立检查

## 1. concat 与 merge 各处理什么

concat 默认按行拼接，例如给映射表追加一条副本；axis=1 时按索引对齐后横向拼接。
merge 根据指定的连接键匹配记录，例如根据 asset 给价格补上名称。
横向拼接的索引对齐与按 asset 匹配不是同一个条件。

## 2. 本次的连接键和匹配关系

asset 是两张表共同的列名，也是本次连接键。每个资产有多天价格，左表 asset 可重复；
正常名称映射中，每个资产代码只对应一行，右表 asset 应唯一，这就是 many_to_one（多对一）。
asset、asset_name 不是 Pandas 特殊名称，必须与实际列名准确对应。

| how | 含义 | 本次左边只有 A/B，右边有 A/B/C |
|---|---|---|
| left | 保留左表出现的连接键 | 只输出 A/B 的记录 |
| inner | 保留两表共同出现的连接键 | 只输出 A/B 的记录 |
| right | 保留右表出现的连接键 | 还会有 C，左侧价格字段缺失 |
| outer | 保留任一表出现的连接键 | 还会有 C，左侧价格字段缺失 |

这份样本 left 与 inner 恰好相同，不表示两种规则相同。
默认 how 是 inner，练习时明确写 how="left"。

## 3. indicator 与未匹配

indicator=True 增加 _merge 列。both 表示键在两边都能匹配，left_only 表示仅在左边，right_only 表示仅在右边。
左连接中不会输出 right_only 记录，不过分类的 value_counts 可能把它列为计数 0。
移除右表 B 的映射后，左侧 B 的四条价格记录保留，名称缺失，_merge 为 left_only。
一般情况下，名称本身也可能为空，因此不能仅凭名称缺失就断定键没匹配；先看 _merge。

## 4. 重复键与行数变化

合并会生成每一对满足连接条件的匹配，不会因为名称文字相同而自动去重。
对一个能匹配的资产，结果行数=左侧该资产行数×右侧该资产行数。
本例正常为 A 的4×1+B的4×1=8；重复A后为4×2+4×1=12。
右侧 C 没有左侧记录，不给左连接结果新增行。
没有任何右侧匹配的左侧记录，在左连接中仍各保留一行。

## 5. validate 的检查范围

validate="many_to_one" 检查右表连接键唯一；"one_to_one" 要求两表键都唯一。
重复键会抛出 MergeError。这个检查不保证所有左侧键都有右侧映射，也不检查名称内容是否正确。
本次只删除 asset 和 asset_name 都相同的副本；同一代码不同名称要核实来源，不能任意保留一个。
本次 asset 均非空。实际检查中也要留意缺失键：Pandas merge 可把两边缺失的键匹配起来。

## 6. iloc[[0]] 与 iloc[0]

iloc[0] 取一行，返回 Series；iloc[[0]] 用行位置列表取一行，返回仍为二维的 DataFrame。
要用 concat 将一条映射作为表格追加时，iloc[[0]] 的形状更直接。
concat 的 ignore_index=True 只重新生成行索引，不删除重复的 asset 值。

## 7. 独立流程的检查点

| 阶段 | 检查内容 | 本次预期 |
|---|---|---|
| 读取 | 列名、形状、样本来源 | 8行5列 |
| 检查 | 类型、缺失、映射键 | 空价格1个；正常映射键无重复 |
| 筛选 | 资产A/B、价格非空且至少100 | 7行，排除105 |
| 分组 | 六项统计，asset普通列 | 2行7列 |
| 合并 | 左连接名称、验证右侧键唯一 | 2行8列 |
| 保存 | 不输出额外索引，日期格式明确 | 最终报告CSV |

独立流程中 A 的 size=count=3，因为空价格记录已被筛掉；保留空价格行的 D11 中 A 是4/3。
两种统计的含义没有改变：size 统计行数，count 统计指定列的非空值。

## 8. 两数之和

返回两个不同下标，不是返回两个数值。重复数值允许，只要下标不同。
seen 是字典，保存之前数值到下标的映射；不是第217题只保存值的集合。
enumerate 同时给出下标和数值。needed=target-number 表示寻找的搭档。
先检查 needed 是否在 seen，再写入当前数字，这样就不会使用当前下标两次。

| 轮次 | index | number | needed | 检查前 seen | 操作 |
|---|---:|---:|---:|---|---|
| 第一次 | 0 | 5 | 5 | {} | 找不到，存入 {5:0} |
| 第二次 | 1 | 5 | 5 | {5:0} | 找到之前下标0，返回[0,1] |

字典查找、写入按平均 O(1) 分析，最多遍历 n 个元素，整体平均时间 O(n)，最坏额外空间 O(n)。
原题保证唯一解且至少两个元素；[3]、目标6的无解检查是本地扩展，返回[]。

## 官方查阅

- [Pandas merge 参数与验证](https://pandas.pydata.org/pandas-docs/version/2.3/reference/api/pandas.merge.html)
- [Pandas 合并指南](https://pandas.pydata.org/pandas-docs/version/2.3/user_guide/merging.html)
- [两数之和原题](https://leetcode.com/problems/two-sum/description/)
- [计划中的莫烦参考课程](https://mofanpy.com/tutorials/data-manipulation/pandas/merge)

课程旧示例中的 DataFrame.append 已在[Pandas 2.0移除](https://pandas.pydata.org/pandas-docs/version/2.0/whatsnew/v2.0.0.html)，不适用于当前 Pandas 2.3，今天用 pd.concat 追加映射副本。
本次只需要理解按共同字段 merge，不必一次学完 join 或复杂索引连接。

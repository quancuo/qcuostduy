"""D10 清洗参考：保留原始证据，输出异常和清洗结果。"""

# 1. 在副本中制造异常
from pathlib import Path  # Path：文件路径
import pandas as pd  # pandas 简写为 pd

data_dir = Path("D:/Learning/study/d10/data")  # 输入样本目录
output_dir = Path("D:/Learning/study/d10/outputs")  # 输出目录
output_dir.mkdir(parents=True, exist_ok=True)  # 创建输出目录，已有则继续

original = pd.read_csv(
    data_dir / "prices_original.csv",
    dtype="string",  # 先把原始内容读成文字
    keep_default_na=False,  # 空字段保持空字符串
)
original_columns = original.columns.tolist()  # 原始五列，后面用于判断完全重复
raw = original.copy()  # 所有异常只加入副本

raw.loc[len(raw)] = ["109", "2026-10-16", "A", "", "1400"]  # 空价格
raw.loc[len(raw)] = ["110", "2026-10-16", "B", "not-a-number", "1000"]  # 非数字价格
raw.loc[len(raw)] = ["111", "2026-02-30", "A", "109", "1500"]  # 非法日期
raw = pd.concat([raw, original.iloc[[0]].copy()], ignore_index=True)  # 完全复制 101
raw.loc[len(raw)] = ["112", "2026-10-13", "A", "999", "1200"]  # 与 103 价格冲突
raw = raw.astype("string")  # 统一保持原始文字类型

provided_dirty = pd.read_csv(
    data_dir / "prices_dirty.csv", dtype="string", keep_default_na=False
)
print("原样本形状：", original.shape)  # (8, 5)
print("异常副本形状：", raw.shape)  # (13, 5)
print("与已准备的脏样本一致：", raw.equals(provided_dirty))  # True
print(raw.tail(5))  # 观察新增的五行

# 2. 保留原始证据，新增转换后的字段
work = raw.copy()  # 在新的工作副本中转换，不改原始文字表
work["source_row"] = range(1, len(work) + 1)  # 输入数据行序号 1～13

work["price_clean"] = pd.to_numeric(
    work["price"].str.strip(), errors="coerce"  # 无法转换的内容变成缺失值
)
work["date_clean"] = pd.to_datetime(
    work["date"].str.strip(), format="%Y-%m-%d", errors="coerce"
)  # 非法日期变成 NaT

print(work[["source_row", "record_id", "date", "date_clean", "price", "price_clean"]])
print(work[["price_clean", "date_clean"]].isna().sum())  # 价格缺失 2，日期缺失 1

# 3. 区分空价格、非数字价格与非法日期
empty_price = work["price"].str.strip().eq("")  # 原始价格为空；eq 表示是否相等
bad_number = work["price_clean"].isna() & ~empty_price  # 非空，但转不成数字
bad_date = work["date_clean"].isna()  # 日期无法解析

work["issue"] = ""  # issue：问题说明
for problem_mask, reason in [  # 逐类给满足条件的行补充说明
    (empty_price, "空价格；"),
    (bad_number, "非数字价格；"),
    (bad_date, "非法日期；"),
]:
    work.loc[problem_mask, "issue"] = work.loc[problem_mask, "issue"] + reason

invalid_mask = empty_price | bad_number | bad_date  # 任一项有问题就隔离
invalid = work.loc[invalid_mask].copy()  # 三行，编号 109、110、111
valid = work.loc[~invalid_mask].copy()  # 其余十行继续检查

print(invalid[["source_row", "record_id", "date", "price", "issue"]])
print("无效记录数：", len(invalid))  # 3
print("继续检查的行数：", len(valid))  # 10

# 4. 完全重复：识别整组，移除多余副本
duplicate_group_mask = valid.duplicated(subset=original_columns, keep=False)
extra_copy_mask = valid.duplicated(subset=original_columns, keep="first")

print("涉及完全重复的记录：")
print(valid.loc[duplicate_group_mask, ["source_row"] + original_columns])  # 数据行 1、12

duplicates = valid.loc[extra_copy_mask].copy()  # 只移除数据行 12 的副本
duplicates["issue"] = "完全重复副本：保留同内容第一条"
unique = valid.loc[~extra_copy_mask].copy()  # 剩余九行

print("移除的完全重复副本数：", len(duplicates))  # 1
print("去重后继续检查：", len(unique))  # 9

# 5. 同一资产同一天，检查有几种价格
grouped_prices = unique.groupby(["asset", "date_clean"])["price_clean"]
price_count = grouped_prices.transform("nunique")  # 每一行对应组内不同价格的数量
conflict_mask = price_count > 1  # 一组有两种及以上价格，说明有冲突

conflicts = unique.loc[conflict_mask].copy()  # 编号 103、112，一起隔离
conflicts["issue"] = "同资产同日期价格冲突：待核实"
clean_work = unique.loc[~conflict_mask].copy()  # 剩余七行进入清洗结果

print(conflicts[["source_row", "record_id", "asset", "date_clean", "price_clean"]])
print("冲突记录数：", len(conflicts))  # 2
print("清洗结果行数：", len(clean_work))  # 7

# 6. 分别导出异常记录与清洗结果
anomalies = pd.concat([invalid, duplicates, conflicts], ignore_index=True)
audit_columns = [  # 输出需要保留的证据字段
    "source_row", "record_id", "date", "asset", "price", "volume",
    "date_clean", "price_clean", "issue",
]
anomalies = anomalies.loc[:, audit_columns].sort_values("source_row").reset_index(drop=True)

clean = clean_work.loc[:, [
    "source_row", "record_id", "date_clean", "asset", "price_clean", "volume"
]].rename(columns={"date_clean": "date", "price_clean": "price"})
clean = clean.sort_values(["asset", "date"]).reset_index(drop=True)

anomalies.to_csv(output_dir / "anomalies.csv", index=False, encoding="utf-8-sig")
clean.to_csv(output_dir / "prices_clean.csv", index=False, encoding="utf-8-sig")

print("异常文件：", output_dir / "anomalies.csv")
print("清洗结果：", output_dir / "prices_clean.csv")
print("输入/异常/清洗：", len(raw), len(anomalies), len(clean))  # 13、6、7
assert len(raw) == len(anomalies) + len(clean)  # assert：核对每一行都有去向
print(clean)

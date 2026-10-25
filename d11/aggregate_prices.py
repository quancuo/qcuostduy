"""D11 分组聚合参考脚本；练习主线请使用 practice.ipynb。"""

from pathlib import Path  # Path：拼接路径；脚本通过自己的位置找到同目录数据
import pandas as pd  # pandas 表格库，简称 pd


def main():  # main：将读取、统计、手算核对和导出过程放在同一个函数中
    # 1. 读取 D11 的练习样本
    base_dir = Path(__file__).resolve().parent  # __file__ 为脚本路径；resolve() 转绝对路径；parent 取所在文件夹
    data_path = base_dir / "data" / "prices.csv"  # / 在 Path 之间用于拼接路径
    output_dir = base_dir / "outputs"  # 之后保存汇总表的文件夹

    df = pd.read_csv(data_path)  # 读取 CSV 为 DataFrame；空价格字段自动识别为缺失
    print(df)  # 查看全部八条记录；编号 105 的 price 应为 NaN
    print("原表形状：", df.shape)  # shape 是属性，预计输出 (8, 5)

    # 2. 确认价格和日期的类型
    df["price"] = pd.to_numeric(  # 将价格列明确转换为数值类型
        df["price"],  # 指定需要转换的原始价格列
        errors="coerce",  # 无法转成数字的值转为缺失值；已有缺失值仍然缺失
    )  # 将转换结果放回 price 列

    df["date"] = pd.to_datetime(  # 将日期文字转换为日期类型
        df["date"],  # 指定需要转换的原始日期列
        format="%Y-%m-%d",  # %Y 年、%m 月、%d 日；例如 2026-10-12
        errors="coerce",  # 非法日期转换为 NaT，即日期缺失值
    )  # 将转换结果放回 date 列

    df.info()  # 查看列、非空数量和类型；直接调用即可，不需要外面再套 print
    print(df.isna().sum())  # isna 标记缺失，再逐列计数；预计 price 为 1，其他为 0

    # 3. 按资产分组，观察 A 组
    grouped = df.groupby("asset")  # 依据 asset 列分组，得到 GroupBy 对象
    print("资产组数：", grouped.ngroups)  # ngroups 是组数，预计输出 2

    a_records = grouped.get_group("A")  # 提取 asset 等于 A 的四条记录
    print(a_records)  # 显示 A 组全部记录，包括价格缺失的那一行
    print("A 组形状：", a_records.shape)  # 仍有四行五列，预计为 (4, 5)

    # 4. 先分别计算六项统计
    record_counts = grouped.size()  # 统计每个资产组的记录行数，含空价格行
    valid_price_counts = grouped["price"].count()  # 统计每组非空价格数
    start_dates = grouped["date"].min()  # 每组最早日期；不需要先按日期排序
    end_dates = grouped["date"].max()  # 每组最晚日期
    highest_prices = grouped["price"].max()  # 每组最高价，忽略价格缺失值
    lowest_prices = grouped["price"].min()  # 每组最低价，忽略价格缺失值

    print("记录数：", record_counts)  # A 为 4，B 为 4
    print("非空价格数：", valid_price_counts)  # A 为 3，B 为 4
    print("起始日期：", start_dates)  # A、B 都是 2026-10-12
    print("结束日期：", end_dates)  # A、B 都是 2026-10-15
    print("最高价：", highest_prices)  # A 为 108，B 为 205
    print("最低价：", lowest_prices)  # A 为 100，B 为 198

    # 5. 用 agg 整理成一张汇总表
    grouped_for_summary = df.groupby(  # 创建用于整理汇总表的分组对象
        "asset",  # 仍根据资产编号分组
        as_index=False,  # 分组键 asset 保持为普通列，结果使用默认数字索引
    )  # 这里尚未执行统计

    summary = grouped_for_summary.agg(  # agg：一次完成并命名多项统计
        record_count=("price", "size"),  # 每组记录数，包含空价格行
        valid_price_count=("price", "count"),  # 每组非空价格数
        start_date=("date", "min"),  # 每组最早日期，覆盖全部记录
        end_date=("date", "max"),  # 每组最晚日期，覆盖全部记录
        highest_price=("price", "max"),  # 每组最高价
        lowest_price=("price", "min"),  # 每组最低价
    )  # 每组整理成一行；结果保存到 summary

    print(summary)  # 查看 A、B 两行汇总结果
    print("汇总表形状：", summary.shape)  # 预计输出 (2, 7)

    # 6. 手算 A，并逐项核对
    manual_a = {  # 字典：保存从纸上独立手算得到的 A 组答案
        "record_count": 4,  # 四条记录，其中一条价格缺失
        "valid_price_count": 3,  # 只有三个价格不是缺失值
        "start_date": pd.Timestamp("2026-10-12"),  # 最早日期
        "end_date": pd.Timestamp("2026-10-15"),  # 最晚日期
        "highest_price": 108,  # 非空价格 100、105、108 中的最大值
        "lowest_price": 100,  # 非空价格 100、105、108 中的最小值
    }  # 字典创建完成

    summary_by_asset = summary.set_index("asset")  # 返回以资产为索引的新表
    a_summary = summary_by_asset.loc["A"]  # 按标签 A 取出该行，得到一个 Series

    for field, expected in manual_a.items():  # 每次取出一个字段名和对应手算值
        actual = a_summary[field]  # 按字段名读取程序统计出的实际值
        print(field, "程序：", actual, "手算：", expected)  # 并列查看两种结果
        assert actual == expected  # assert：实际值不相等时停止并报错，帮助发现问题

    print("A 组的六项统计与手算一致。")  # 前面六项全部相等才会执行到这里

    # 7. 导出汇总表，并检查总数
    output_dir.mkdir(  # 创建保存结果的文件夹
        parents=True,  # 上级文件夹不存在时一并创建
        exist_ok=True,  # 文件夹已经存在时继续执行
    )  # 此时输出文件夹已准备好

    summary_path = output_dir / "asset_summary.csv"  # 拼接结果文件的完整路径
    summary.to_csv(  # 将汇总表写成 CSV 文件
        summary_path,  # 输出文件路径
        index=False,  # 不输出额外的默认索引列；asset 普通列仍保留
        encoding="utf-8-sig",  # 采用带标记的 UTF-8 编码
        date_format="%Y-%m-%d",  # 日期输出为例如 2026-10-12
    )  # CSV 保存完成

    print("结果保存位置：", summary_path)  # 显示刚保存的结果路径
    print("记录数合计：", summary["record_count"].sum())  # 预计为 8
    print("非空价格数合计：", summary["valid_price_count"].sum())  # 预计为 7
    print("原表仍有多少行：", len(df))  # 原表仍为八行，聚合不会删除原表记录

if __name__ == "__main__":  # 直接运行本文件时才调用 main；导入时不执行整个流程
    main()  # 开始执行 D11 的完整参考过程

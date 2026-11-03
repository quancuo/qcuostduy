"""D12 独立流程参考脚本：读取、检查、筛选、分组、合并、保存。"""

from pathlib import Path  # Path：处理文件路径
import pandas as pd  # pandas 表格处理库，简称 pd


def main():  # 将整个独立流程放在 main 函数里
    base_dir = Path(__file__).resolve().parent  # __file__是脚本路径；resolve转绝对路径；parent取所在目录

    prices_check = pd.read_csv(base_dir / "data" / "prices.csv")  # 从文件重新读取价格，不依赖前面实验的变量
    names_check = pd.read_csv(base_dir / "data" / "asset_names.csv")  # 读取正常、键唯一的名称映射表

    prices_check["price"] = pd.to_numeric(  # 将价格转换为数值
        prices_check["price"],  # 需要转换的价格列
        errors="coerce",  # 无法转换的价格变成缺失值
    )  # 转换结果写回价格列
    prices_check["date"] = pd.to_datetime(  # 将日期转换为日期类型
        prices_check["date"],  # 需要转换的日期列
        format="%Y-%m-%d",  # 按 年-月-日 解析
        errors="coerce",  # 非法日期变成 NaT
    )  # 转换结果写回日期列

    print("读取后形状：", prices_check.shape)  # 预计 (8, 5)
    print(prices_check.isna().sum())  # 价格缺失 1 个，其他列缺失 0 个
    print("映射键是否重复：", names_check["asset"].duplicated().any())  # 预计 False

    selection = (  # selection：记录每一行是否符合本次筛选要求的布尔 Series
        prices_check["asset"].isin(["A", "B"])  # 资产必须是 A 或 B；isin 表示是否属于给定列表
        & prices_check["price"].notna()  # 价格必须非空；notna 表示不是缺失值
        & (prices_check["price"] >= 100)  # 价格至少为 100；组合条件时给比较式加括号
    )  # 三个条件都成立时，整行标记才为 True
    filtered = prices_check.loc[selection].copy()  # 保留满足条件的记录，并创建独立副本
    print("筛选后形状：", filtered.shape)  # 预计 (7, 5)，编号 105 被排除

    summary = filtered.groupby(  # 在筛选结果上按资产分组
        "asset",  # 分组键为资产代码
        as_index=False,  # 让 asset 仍是普通列，方便随后 merge
    ).agg(  # 一次计算六项统计，并给结果列命名
        record_count=("price", "size"),  # 筛选后每组记录数：A 为 3，B 为 4
        valid_price_count=("price", "count"),  # 非空价格数：A 为 3，B 为 4
        start_date=("date", "min"),  # 每组最早日期
        end_date=("date", "max"),  # 每组最晚日期
        highest_price=("price", "max"),  # 每组最高价
        lowest_price=("price", "min"),  # 每组最低价
    )  # 汇总后预计两行七列

    final_summary = pd.merge(  # 给汇总表补充资产名称
        summary,  # 左表：按资产汇总的两行
        names_check,  # 右表：资产代码与名称映射
        on="asset",  # 按共同的 asset 列匹配
        how="left",  # 保留左表中 A、B 的汇总结果
        validate="many_to_one",  # 检查右表每个资产代码最多一行
    )  # 结果预计两行八列，新增一列 asset_name
    print(final_summary)  # 查看最终汇总表
    print("合并前后行数：", len(summary), len(final_summary))  # 预计 2、2

    output_dir = base_dir / "outputs"  # 设置输出文件夹
    output_dir.mkdir(parents=True, exist_ok=True)  # 上级目录也可创建；已存在时继续
    report_path = output_dir / "asset_summary_with_names.csv"  # 拼接报告文件路径
    final_summary.to_csv(  # 导出本次独立流程的最终结果
        report_path,  # 输出到指定报告文件
        index=False,  # 不保存额外的默认行索引
        encoding="utf-8-sig",  # 使用便于 Windows 软件识别的 UTF-8 编码
        date_format="%Y-%m-%d",  # 日期输出为 年-月-日
    )  # 报告保存完成
    print("最终报告：", report_path)  # 显示结果文件的位置


if __name__ == "__main__":  # 直接运行脚本时才执行；导入时不自动生成报告
    main()  # 开始运行完整流程

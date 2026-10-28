"""D13参考流程；全部输入为模拟教学数据。"""


def main():  # 将手算、收益计算和缺失实验放在主函数中
    # 1. 先在纸上手算 100 → 110 → 99
    up_return = 110 / 100 - 1  # 第一段简单收益率：本期价格除以上期价格，再减一
    down_return = 99 / 110 - 1  # 第二段的上期价格是110，所以分母改为110
    whole_return = 99 / 100 - 1  # 从最初100到最终99的整个区间收益率

    print("第一段：", up_return)  # 约0.10，浮点数可能显示少量尾数
    print("第二段：", down_return)  # 约-0.10
    print("整个区间：", whole_return)  # 约-0.01
    print(f"第一段：{up_return:.2%}")  # f字符串中的.2%：按百分比显示，并保留两位小数
    print(f"第二段：{down_return:.2%}")  # 显示-10.00%，不改变变量里保存的小数
    print(f"整个区间：{whole_return:.2%}")  # 显示-1.00%

    # 2. 用 shift 与 pct_change 对照手算
    import pandas as pd  # pandas表格处理库，通常简称pd

    demo = pd.DataFrame({"price": [100, 110, 99]})  # 建立三行一列的小样本
    demo["prev_price"] = demo["price"].shift(1)  # prev是previous的缩写，表示前一条价格
    demo["return_formula"] = demo["price"] / demo["prev_price"] - 1  # 直接按公式计算
    demo["return_pct"] = demo["price"].pct_change(  # 用Pandas方法计算同样的变化率
        fill_method=None,  # None：不要在计算前自动填充缺失价格
    )  # 预计为NaN、0.10、-0.10；返回值仍是小数

    print(demo)  # 对照价格、前值、两种计算结果
    print(demo.shape)  # 预计(3,4)，增加了前值和两列收益率

    # 3. 读取乱序的多资产教学数据，检查后排序
    from pathlib import Path  # Path：表示和拼接文件路径

    base_dir = Path(__file__).resolve().parent  # __file__为脚本路径；resolve转绝对路径；parent取所在目录
    raw = pd.read_csv(base_dir / "data" / "prices.csv")  # 读取六条乱序的模拟价格
    raw["date"] = pd.to_datetime(raw["date"], format="%Y-%m-%d", errors="coerce")  # 转换日期
    raw["price"] = pd.to_numeric(raw["price"], errors="coerce")  # 转换价格，失败变缺失

    print(raw)  # 先观察原来的乱序
    raw.info()  # 查看列类型和非空数
    print(raw.isna().sum())  # 完整样本三列缺失数都应为0
    duplicate_key = raw.duplicated(subset=["asset", "date"], keep=False)  # 标记同资产同日重复
    print("重复键行数：", int(duplicate_key.sum()))  # 预计0
    print("非正价格行数：", int((raw["price"] <= 0).sum()))  # 预计0，零不能作为收益公式分母

    assert raw[["asset", "date", "price"]].notna().all().all()  # 确认这份完整样本关键字段均非空
    assert not duplicate_key.any()  # 一项资产一天只能有一条价格，避免前值含义不明确
    assert (raw["price"] > 0).all()  # 本份收盘价样本要求价格为正

    prices = raw.sort_values(["asset", "date"]).reset_index(drop=True)  # 先排资产，再排日期，并重建行索引
    print(prices)  # 预计先是A的三天，再是B的三天
    print(prices.shape)  # 排序不删除记录，仍为(6,3)

    # 4. 在每个资产内部取得前一条价格和日期
    prices["prev_price"] = prices.groupby("asset")["price"].shift(1)  # 每个资产内部的前一条价格
    prices["prev_date"] = prices.groupby("asset")["date"].shift(1)  # 每个资产内部的前一条记录日期
    prices["return_formula"] = prices["price"] / prices["prev_price"] - 1  # 按本期/上期-1计算

    print(prices[["asset", "date", "price", "prev_date", "prev_price", "return_formula"]])  # 逐行核对分母和日期
    print("没有前值的行：")  # 下方在本完整样本中应是A、B各一条首行
    print(prices.loc[prices["prev_price"].isna(), ["asset", "date"]])  # 用布尔筛选查看组首

    # 5. 使用分组 pct_change，并与公式核对
    prices["return_pct"] = prices.groupby("asset")["price"].pct_change(  # 在各资产内部计算相邻观测收益
        fill_method=None,  # 不自动填充缺失价格
    )  # 返回的小数与按公式得到的收益率对应

    print(prices[["asset", "date", "price", "prev_price", "return_formula", "return_pct"]])  # 比较两种方法
    print("两种结果是否一致：", prices["return_formula"].equals(prices["return_pct"]))  # 本例预计True
    print("仅按百分数数值显示：", (prices["return_pct"] * 100).round(2))  # 10表示10%，底层收益列仍保存0.1

    # 6. 错误对照：为什么不能全表直接计算
    wrong_global = prices[["asset", "date", "price"]].copy()  # 创建错误演示专用副本，不修改正确结果
    wrong_global["wrong_return"] = wrong_global["price"].pct_change(fill_method=None)  # 故意漏掉groupby
    print(wrong_global.loc[wrong_global["asset"] == "B"].head(1))  # B首行得到错误的跨资产变化率

    # 7. 记录存在，但中间价格缺失
    missing_value = pd.read_csv(base_dir / "data" / "prices_missing_value.csv")  # 读取记录存在但价格为空的样本
    missing_value["date"] = pd.to_datetime(missing_value["date"], format="%Y-%m-%d")  # 转换日期
    missing_value["price"] = pd.to_numeric(missing_value["price"], errors="coerce")  # 空价格保持缺失
    missing_value = missing_value.sort_values(["asset", "date"]).reset_index(drop=True)  # 排好组内时间顺序
    missing_value["prev_price"] = missing_value.groupby("asset")["price"].shift(1)  # 前一条为空就保留为空
    missing_value["return_pct"] = missing_value.groupby("asset")["price"].pct_change(fill_method=None)  # 不填补价格

    print(missing_value.loc[missing_value["asset"] == "A"])  # A三条return_pct都为NaN
    print(missing_value.shape)  # 仍有六行，新增两列后为(6,5)

    # 8. 整条交易记录缺失：观察收益的实际日期区间
    missing_row = pd.read_csv(base_dir / "data" / "prices_missing_row.csv")  # 读取缺少A中间整条记录的样本
    missing_row["date"] = pd.to_datetime(missing_row["date"], format="%Y-%m-%d")  # 转换日期
    missing_row["price"] = pd.to_numeric(missing_row["price"], errors="coerce")  # 转换价格
    missing_row = missing_row.sort_values(["asset", "date"]).reset_index(drop=True)  # 按资产和日期排序
    missing_row["prev_price"] = missing_row.groupby("asset")["price"].shift(1)  # A的99对应的前价变成100
    missing_row["prev_date"] = missing_row.groupby("asset")["date"].shift(1)  # A的10月14日前一观测日为10月12日
    missing_row["return_pct"] = missing_row.groupby("asset")["price"].pct_change(fill_method=None)  # 计算相邻观测收益

    print(missing_row.loc[missing_row["asset"] == "A"])  # 重点观察prev_date、prev_price及-0.01
    print("输入记录数：", len(missing_row))  # 预计5，缺的是一整行

    # 9. 用教学交易日序号标记跨交易区间
    calendar = pd.read_csv(base_dir / "data" / "trading_calendar.csv")  # 读取三天教学日历
    calendar["date"] = pd.to_datetime(calendar["date"], format="%Y-%m-%d")  # 转换日历日期
    gap_audit = pd.merge(  # 给缺行样本补充每个日期对应的交易日序号
        missing_row,  # 左表：五条实际观测记录
        calendar,  # 右表：日期对应session_no
        on="date",  # 根据日期匹配
        how="left",  # 保留实际观测记录，不自动补出缺失行
        validate="many_to_one",  # 日历中的每个日期必须唯一
    )  # 合并后仍然五行
    gap_audit = gap_audit.sort_values(["asset", "date"]).reset_index(drop=True)  # 明确组内观测顺序
    assert gap_audit["session_no"].notna().all()  # 本例每条观测日期都必须能在教学日历中找到
    previous_session = gap_audit.groupby("asset")["session_no"].shift(1)  # 同一资产前一观测的交易日序号
    gap_audit["session_gap"] = gap_audit["session_no"] - previous_session  # 计算相邻观测跨几个交易区间
    gap_audit["return_one_session"] = gap_audit["return_pct"].where(  # 单独保留只跨一个交易区间的收益
        gap_audit["session_gap"] == 1,  # 只有序号差为1才保留；其余置为缺失
    )  # 原始相邻观测收益return_pct保持不变，便于核对

    print(gap_audit[["asset", "prev_date", "date", "return_pct", "session_gap", "return_one_session"]])  # 查看收益区间

    # 10. 选做：补齐日期不等于补出真实价格
    a_observed = missing_row.loc[missing_row["asset"] == "A", ["date", "price"]].copy()  # 只取A的两条实际观测
    a_calendar = pd.merge(  # 以教学日历为左表补出日期
        calendar[["date"]],  # 三个完整的教学交易日
        a_observed,  # A只有两个日期有价格
        on="date",  # 根据日期匹配
        how="left",  # 保留日历中的三天
        validate="one_to_one",  # 两边每个日期都必须唯一
    )  # 缺少的10月13日出现，但价格仍然缺失
    a_calendar["return_pct"] = a_calendar["price"].pct_change(fill_method=None)  # 只含A，直接对该价格序列计算
    print(a_calendar)  # 三条收益都无法计算，不能用补日期替代找回价格

    # 11. 保存正确结果，独立复写核心流程
    output_dir = base_dir / "outputs"  # 设置结果文件夹
    output_dir.mkdir(parents=True, exist_ok=True)  # 上级目录可一并创建，已存在则继续

    prices.to_csv(  # 保存完整样本的正确收益计算，不保存错误对照
        output_dir / "returns.csv",  # 六行七列，包含前值和两种收益率
        index=False,  # 不另存默认数字行索引
        encoding="utf-8-sig",  # 使用方便Windows识别的编码
        date_format="%Y-%m-%d",  # 日期和前一日期均按年-月-日输出
    )  # 完整样本结果保存完毕
    missing_value.to_csv(  # 保存六行的缺价格对照
        output_dir / "missing_value_returns.csv",  # A三条收益都缺失，B不受影响
        index=False,  # 不输出额外索引
        encoding="utf-8-sig",  # 使用带标记的UTF-8编码
        date_format="%Y-%m-%d",  # 日期按年-月-日输出
    )  # 缺价格对照保存完毕
    gap_audit.to_csv(  # 保存五行的缺整行区间核对
        output_dir / "missing_row_audit.csv",  # 同时保存跨观测收益和只跨一交易区间的收益
        index=False,  # 不输出额外索引
        encoding="utf-8-sig",  # 使用带标记的UTF-8编码
        date_format="%Y-%m-%d",  # 日期列使用一致格式
    )  # 区间核对表保存完毕

    print("完整样本结果形状：", prices.shape)  # 预计(6,7)
    print("缺价格结果形状：", missing_value.shape)  # 预计(6,5)
    print("缺整行核对形状：", gap_audit.shape)  # 预计(5,9)
    print("结果文件夹：", output_dir)  # 显示保存位置


if __name__ == "__main__":  # 直接运行本文件才执行，导入时不自动写结果
    main()  # 运行完整的D13参考流程

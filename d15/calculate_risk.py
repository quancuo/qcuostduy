"""D15参考：非年化收益标准差、历史峰值、负值回撤及正幅度。"""


def main():  # 直接运行时调用完整流程
    # 1. 先手算四个价格，确认正负号
    import pandas as pd  # pandas用于表格和序列计算，简称pd

    demo = pd.DataFrame({"price": [100, 90, 108, 81]})  # 四个价格构成一列
    demo["wealth"] = demo["price"] / demo["price"].iloc[0]  # iloc[0]取首条价格；净值从1开始
    demo["peak"] = demo["wealth"].cummax()  # cummax：从开头到当前行的累计最大值
    demo["drawdown"] = demo["wealth"] / demo["peak"] - 1  # 回撤采用非正值口径
    demo_signed_min = demo["drawdown"].min()  # min取最负的回撤，预计-0.25
    demo_mdd = -demo_signed_min  # mdd是maximum drawdown缩写，此处用正的幅度0.25

    print(demo)  # 先对照自己手算的四行
    print(f"最大回撤负值：{demo_signed_min:.2%}")  # .2%只格式化显示为-25.00%
    print(f"最大回撤幅度：{demo_mdd:.2%}")  # 预计25.00%，变量内部仍为0.25
    assert abs(demo_mdd - 0.25) < 1e-12  # abs为绝对值；容许极小浮点误差


    # 2. 从原CSV重新读取并检查
    from pathlib import Path  # Path代表文件路径，/可连接文件夹和文件名

    base_dir = Path(__file__).resolve().parent  # 今天D15练习所在目录
    raw = pd.read_csv(base_dir / "data" / "prices.csv")  # 从原文件读取12行3列
    raw["date"] = pd.to_datetime(raw["date"], format="%Y-%m-%d", errors="coerce")  # 非法日期转为NaT
    raw["price"] = pd.to_numeric(raw["price"], errors="coerce")  # 非数字价格转为缺失值；coerce须加引号

    assert raw[["asset", "date", "price"]].notna().all().all()  # 先逐列再整体检查关键字段非空
    duplicate_key = raw.duplicated(subset=["asset", "date"], keep=False)  # subset指定检查重复的两列
    assert not duplicate_key.any()  # assert not表示要求“不存在任何重复键”
    assert (raw["price"] > 0).all()  # 要求每个价格都大于0，才做本课价格比值
    prices = raw.sort_values(["asset", "date"]).reset_index(drop=True)  # 整表先按资产、再按日期升序排列

    print(prices)  # 核对A/B各六条，避免资产与价格发生错配
    print(prices.shape)  # 此时预计(12, 3)


    # 3. 收益标准差：仅使用五个有效收益
    prices["return_pct"] = prices.groupby("asset")["price"].pct_change(fill_method=None)  # 在各资产内计算本期/上期-1
    return_count = prices.groupby("asset")["return_pct"].count()  # count只统计非空收益，预计A/B各5个
    return_std = prices.groupby("asset")["return_pct"].std(ddof=1)  # 各资产收益的样本标准差，得到带资产索引的Series

    print(prices[["asset", "date", "price", "return_pct"]])  # 每个资产首行收益仍应是NaN
    print(return_count)  # 预计A=5、B=5
    for asset, value in return_std.items():  # items依次取出资产标签和对应标准差
        print(asset, f"非年化收益标准差：{value:.4%}")  # 预计A约8.1084%，B约5.6520%


    # 4. 每个资产首价归一化为1
    first_price = prices.groupby("asset")["price"].transform("first")  # A组每行为100，B组每行为200，长度仍为12
    prices["wealth"] = prices["price"] / first_price  # 每行除以本资产首价，各资产第一行恰好为1

    print(prices[["asset", "date", "price", "wealth"]])  # A末期1.08，B末期1.075


    # 5. 组内历史峰值与回撤
    prices["peak"] = prices.groupby("asset")["wealth"].cummax()  # 分资产逐行更新截至当期的最高净值
    prices["drawdown"] = prices["wealth"] / prices["peak"] - 1  # 当前净值相对此前及当前峰值的下降，结果非正

    print(prices[["asset", "date", "wealth", "peak", "drawdown"]])  # 检查峰值不下降、回撤不为正
    assert (prices["drawdown"] <= 1e-12).all()  # 容许计算误差；本完整正价样本回撤应不大于0


    # 6. 汇总风险口径，区分负值与正幅度
    summary = prices.groupby("asset").agg(  # 每个资产聚合为一行；括号中的名称是自己给结果列起的名字
        price_count=("price", "size"),  # size统计本组记录行数，预计6
        return_count=("return_pct", "count"),  # count统计非空收益数，预计5
        min_drawdown=("drawdown", "min"),  # min取本组最深的负回撤
    )  # summary暂以asset为索引
    summary["return_std"] = return_std  # 放入前面算好的非年化样本标准差，按资产索引对齐
    summary["max_drawdown_magnitude"] = -summary["min_drawdown"]  # 将最负回撤取负号，得到正的最大回撤幅度

    print(summary)  # A幅度0.10，B幅度0.05；不要提前把这些小数改成10和5
    for asset, row in summary.iterrows():  # iterrows逐行取出资产标签和一行结果，这里仅用于两行展示
        print(asset, f"最大回撤负值：{row['min_drawdown']:.2%}", f"幅度：{row['max_drawdown_magnitude']:.2%}")  # 格式化显示


    # 7. 画负值回撤曲线，并另存结果
    import matplotlib.pyplot as plt  # pyplot是Matplotlib的绘图接口，简称plt
    import matplotlib.dates as mdates  # dates是日期刻度工具，简称mdates
    from matplotlib.ticker import PercentFormatter  # 用于把小数坐标显示为百分数

    output_dir = base_dir / "outputs"  # output_dir表示输出文件夹路径
    output_dir.mkdir(parents=True, exist_ok=True)  # 缺少父文件夹就一起创建；已有时不报错
    fig, ax = plt.subplots(figsize=(9, 4.8))  # 创建一张画布fig和一个坐标区域ax，尺寸单位为英寸
    for asset, group in prices.groupby("asset"):  # 每轮group是一种资产的六行子表
        ax.plot(group["date"], group["drawdown"], marker="o", label=asset)  # 画该资产的非正值回撤，保留小数
    ax.axhline(0, color="gray", linestyle="--", linewidth=1)  # 添加0%参考线
    ax.set_title("Drawdown by asset (drawdown <= 0)")  # 标题说明回撤采用非正值
    ax.set_xlabel("Observation date")  # 横轴为观测日期
    ax.set_ylabel("Drawdown (%, non-positive)")  # 纵轴单位和正负号口径
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))  # 0.10显示10%，-0.10显示-10%
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))  # 日期标签显示月-日
    ax.legend(title="Asset")  # 根据每条plot的label显示资产图例
    ax.grid(alpha=0.3)  # 网格用较浅的透明度，便于读数
    fig.autofmt_xdate(rotation=30)  # 旋转日期文字，减少重叠
    fig.tight_layout()  # 调整布局，避免标题或坐标标签被挤出画布
    fig.savefig(output_dir / "drawdown.png", dpi=150, bbox_inches="tight")  # 保存PNG图像
    plt.close(fig)  # 脚本只保存图像，关闭画布以免等待窗口

    prices.to_csv(output_dir / "risk_detail.csv", index=False, encoding="utf-8-sig")  # 保存12行明细，不导出默认索引
    summary.reset_index().to_csv(output_dir / "risk_summary.csv", index=False, encoding="utf-8-sig")  # 资产索引转为列后保存
    demo.to_csv(output_dir / "drawdown_check.csv", index=False, encoding="utf-8-sig")  # 保存四价格手算核对表
    print("已保存：", output_dir)  # 查看CSV与PNG所在文件夹


if __name__ == "__main__":  # 导入时不自动生成输出
    main()  # 运行参考计算和绘图

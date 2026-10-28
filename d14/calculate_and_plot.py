"""D14参考脚本：计算累计收益、MA3，保存CSV与两张图。"""


def main():  # 将读取、计算和绘图过程放入主函数
    # 1. 手算累计收益：为什么要连乘
    import pandas as pd  # pandas表格处理库，简称pd

    demo_returns = pd.Series([0.10, -0.10], name="period_return")  # 两段已知收益，小数形式
    demo_factors = 1 + demo_returns  # 每段价值倍数：1.10、0.90
    demo_wealth = demo_factors.cumprod(skipna=False)  # cumprod累计连乘，得到1.10、0.99
    demo_cumulative = demo_wealth - 1  # 净值倍数减1，得到累计收益0.10、-0.01

    print(demo_returns.sum())  # 简单相加为0，不能替代两段累计收益
    print(demo_wealth)  # 查看每段结束时的价值倍数
    print(demo_cumulative)  # 查看每段结束时的累计收益
    print(f"两段累计收益：{demo_cumulative.iloc[-1]:.2%}")  # 预计-1.00%；.iloc[-1]取最后一个结果

    # 2. 读取并检查六期模拟价格
    from pathlib import Path  # Path用于拼接文件路径

    base_dir = Path(__file__).resolve().parent  # __file__是脚本路径；resolve转绝对路径；parent取所在目录
    raw = pd.read_csv(base_dir / "data" / "prices.csv")  # 读取十二条模拟价格
    raw["date"] = pd.to_datetime(raw["date"], format="%Y-%m-%d", errors="coerce")  # 转换日期
    raw["price"] = pd.to_numeric(raw["price"], errors="coerce")  # 转换数值价格

    print(raw.shape)  # 预计(12,3)
    print(raw.isna().sum())  # 本次完整样本各列缺失数都应为0
    duplicate_key = raw.duplicated(subset=["asset", "date"], keep=False)  # 仅比较资产和日期是否重复
    assert raw[["asset", "date", "price"]].notna().all().all()  # 本份完整样本要求关键字段均非空
    assert not duplicate_key.any()  # 要求没有同资产同日期重复记录
    assert (raw["price"] > 0).all()  # 本份模拟收盘价均为正数

    prices = raw.sort_values(["asset", "date"]).reset_index(drop=True)  # 先排资产，再排日期，并重建默认索引
    print(prices)  # A六期100/110/99/105/102/108，B六期200/190/209/205/210/215

    # 3. 计算每期收益，设置累计指标的起点
    prices["return_pct"] = prices.groupby("asset")["price"].pct_change(fill_method=None)  # 每个资产内部计算收益
    prices["growth_factor"] = 1 + prices["return_pct"]  # growth_factor：每期价值倍数
    first_in_asset = prices.groupby("asset").cumcount() == 0  # 标记每个资产组内的第一条记录
    prices.loc[first_in_asset, "growth_factor"] = 1.0  # 仅初始化累计指标的基准倍数，不修改原始收益列

    print(prices[["asset", "date", "price", "return_pct", "growth_factor"]])  # 比较原始首行缺失和基准倍数1

    # 4. 分资产累计连乘，并用价格比值独立核对
    prices["wealth_index"] = prices.groupby("asset")["growth_factor"].cumprod(  # 各资产内部累计连乘价值倍数
        skipna=False,  # 如果中间缺失，从缺口起保留未知，不自动跨过
    )  # 每个资产首行从1开始
    prices["cumulative_return"] = prices["wealth_index"] - 1  # 起始累计收益为0，此后表示相对首价的变化

    first_price = prices.groupby("asset")["price"].transform("first")  # 给每一行对应本资产的首条价格
    prices["return_from_price"] = prices["price"] / first_price - 1  # 用首尾价格比直接核对
    maximum_error = (prices["cumulative_return"] - prices["return_from_price"]).abs().max()  # 计算最大绝对误差
    print("两种累计计算的最大差异：", maximum_error)  # 预计为0或极小浮点误差
    assert maximum_error < 1e-10  # 1e-10表示10的负10次方，用作本例核对容差

    print(prices[["asset", "date", "wealth_index", "cumulative_return", "return_from_price"]])  # A第三期为-1%，末期8%；B末期7.5%

    # 5. 用三期小例子理解滚动均值
    demo_prices = pd.Series([100, 110, 99, 105], name="price")  # 用四条价格观察窗口如何移动
    demo_ma3 = demo_prices.rolling(  # rolling创建滚动窗口
        window=3,  # 每个窗口取最近三条观测
        min_periods=3,  # 至少三个非空价格才输出结果
    ).mean()  # 对每个窗口求算术平均数

    print(demo_ma3)  # 预计NaN、NaN、103、104.6667

    # 6. 在各资产内部计算MA3
    prices["ma3"] = prices.groupby("asset")["price"].transform(  # 分资产计算，并保持与原行对齐
        lambda s: s.rolling(window=3, min_periods=3).mean()  # s是一组价格；滚动三条后求每个窗口的均值
    )  # 返回的每一条均价放到对应的资产和日期行

    print(prices[["asset", "date", "price", "ma3"]])  # 检查每个资产前两行都为NaN
    print("均价缺失总数：", int(prices["ma3"].isna().sum()))  # 预计4，A/B各2条

    # 7. 绘制A/B累计收益曲线
    import matplotlib.pyplot as plt  # pyplot绘图接口，简称plt
    import matplotlib.dates as mdates  # 日期坐标格式工具，简称mdates

    output_dir = base_dir / "outputs"  # 设置图表和CSV的输出文件夹
    output_dir.mkdir(parents=True, exist_ok=True)  # 必要时创建目录，已经存在则继续
    plot_dates = prices["date"].drop_duplicates().sort_values()  # 本次六个不同的观测日期

    fig, ax = plt.subplots(figsize=(8, 4.8))  # fig是整张图，ax是坐标区域；尺寸单位为英寸
    for asset, group in prices.groupby("asset"):  # 每轮取一项资产代码和该资产的整张子表
        ax.plot(  # 将这一项资产画成一条折线
            group["date"],  # 横坐标：该资产的日期
            group["cumulative_return"] * 100,  # 纵坐标：只在绘图时转换为百分数数值
            marker="o",  # 用圆点标记每个观测日期
            label=f"Asset {asset}",  # 图例名称，例如Asset A
        )  # 当前资产曲线添加完成

    ax.set_title("Cumulative returns from first price")  # 标题说明以首条价格为基准
    ax.set_xlabel("Date")  # 横轴名称
    ax.set_ylabel("Cumulative return (%)")  # 纵轴名称和百分比单位
    ax.set_xticks(plot_dates)  # 明确显示六个观测日期刻度
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))  # 日期刻度简写为月-日
    ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)  # 画零累计收益参考线
    ax.grid(alpha=0.3)  # 淡色网格，alpha控制透明度
    ax.legend()  # 显示每条曲线label对应的图例
    fig.autofmt_xdate(rotation=30)  # 旋转日期文字，减少重叠
    fig.tight_layout()  # 调整布局，避免标题与轴标签被裁切
    fig.savefig(output_dir / "cumulative_returns.png", dpi=150, bbox_inches="tight")  # 保存PNG图片
    plt.close(fig)  # 脚本保存后关闭图像，不等待交互窗口

    # 8. 绘制A的价格与三期均线
    a_prices = prices.loc[prices["asset"] == "A"].copy()  # 取出A的六条价格与计算结果
    fig, ax = plt.subplots(figsize=(8, 4.8))  # 创建新的独立图像和坐标区域
    ax.plot(a_prices["date"], a_prices["price"], marker="o", label="Price")  # 绘制A价格曲线
    ax.plot(a_prices["date"], a_prices["ma3"], marker="s", linestyle="--", label="MA3")  # 绘制A三期均线
    ax.set_title("Asset A price and 3-observation mean")  # 标题，强调三条观测均值
    ax.set_xlabel("Date")  # 横轴为日期
    ax.set_ylabel("Price (sample units)")  # 纵轴为样本价格单位
    ax.set_xticks(plot_dates)  # 显示本次六个观测日期
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))  # 日期显示为月-日
    ax.grid(alpha=0.3)  # 添加淡色网格
    ax.legend()  # 显示Price与MA3图例
    fig.autofmt_xdate(rotation=30)  # 旋转日期标签
    fig.tight_layout()  # 调整边距，避免文字裁切
    fig.savefig(output_dir / "price_ma3_A.png", dpi=150, bbox_inches="tight")  # 保存价格均线图
    plt.close(fig)  # 脚本保存后关闭图像，不等待交互窗口

    # 9. 保存计算表并核对末期结果
    prices.to_csv(  # 保存完整计算表
        output_dir / "returns_and_ma3.csv",  # 十二行九列的参考结果
        index=False,  # 不另存默认数字索引
        encoding="utf-8-sig",  # 使用方便Windows识别的编码
        date_format="%Y-%m-%d",  # 日期输出为年-月-日
    )  # CSV保存完成
    print(prices.groupby("asset").tail(1)[["asset", "date", "cumulative_return", "ma3"]])  # 查看各资产末条结果
    print(prices.shape)  # 预计(12,9)
    print("结果文件夹：", output_dir)  # 显示CSV和两张图的保存位置


if __name__ == "__main__":  # 直接运行才执行，不在导入时生成文件
    main()  # 开始执行参考流程

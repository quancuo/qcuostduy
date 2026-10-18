1. 为什么每日总时长使用 axis=1？

2. 为什么各主题总时长使用 axis=0？

3. topic_means 的 shape 是什么？
   与 minutes 相减时怎样对齐？

4. centered 中的负数表示什么？

5. Figure 和 Axes 分别是什么？
Figure：整张图的画布，对应 fig。
Axes：画布中的一个绘图区，对应 ax，包含曲线、标题、横纵坐标等
ax.plot(days, daily_totals)    # 在绘图区中画线
ax.set_title("Daily study time")

fig.savefig("daily_minutes.png")  # 保存整张图

6. 绘图横、纵坐标分别保存什么？
   为什么它们的元素数量需要对应？

7. 动态和为什么要在每次累加后，把 total 追加到结果中？
def filter_with_while(minutes, minimum):
    selected = []
    index = 0

    # 这里故意保留一个逻辑错误，供断点练习
    while index < len(minutes):
        duration = minutes[index]

        if duration >= minimum:
            selected.append(duration)

        index = index + 1

    return selected


minutes = [20, 45, 30, 45, 60]

result = filter_with_while(minutes, 30)
print("筛选结果 =", result)

# 空列表：没有记录
print("空列表 =", filter_with_while([], 30))

# 只有一项，而且满足条件
print("单项满足 =", filter_with_while([60], 30))

# 只有一项，但不满足条件
print("单项不满足 =", filter_with_while([20], 30))

# 恰好等于筛选门槛
print("恰好达到门槛 =", filter_with_while([30], 30))
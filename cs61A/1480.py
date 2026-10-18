def running_sum(nums):
    # running_sum：动态和，也就是累计和
    # nums：输入的数字列表
    total = 0
    result = []

    for number in nums:
        total = total + number
        result.append(total)

    return result


print(running_sum([2, 5, -1, 4]))
print(running_sum([3]))
print(running_sum([0, 0, 0]))
print(running_sum([-2, -1, 3]))


def sum(nums):
    total = 0
    result = []                  # 创建空列表，用来保存每一步的累计和

    for x in nums:
        total += x               # 将当前数字 x 加入累计和；等价于 total = total + x
        result.append(total)     # 将更新后的累计和追加到结果列表末尾
      
    return result                # 所有数字处理完后，将完整结果列表返回给调用者

print(sum([2, 5, -1, 4]))
print(sum([3]))
print(sum([0, 0, 0]))
print(sum([-2, -1, 3]))
    
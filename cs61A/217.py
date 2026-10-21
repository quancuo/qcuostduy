"""217 参考实现：请先在 d9/practice.ipynb 独立完成，再对照复习。"""

def contains_duplicate(nums):  # 判断输入数字列表是否存在重复值
    seen = set()  # seen：已经见过的数字；set() 创建空集合

    for number in nums:  # 按顺序检查列表中的每个数字
        if number in seen:  # in：判断这个数字是否已在集合中
            return True  # 已经出现过，说明存在重复，立即返回 True
        seen.add(number)  # add：把第一次见到的数字加入集合

    return False  # 全部检查完仍无重复，返回 False；这句位于循环外


if __name__ == "__main__":  # 直接运行本文件时执行检查
    examples = [  # 输入和预期结果
        ([2, 5, 2], True),
        ([2, 5, 7], False),
        ([7], False),
        ([1, 1], True),
    ]
    for nums, expected in examples:  # 逐组取出输入和预期结果
        result = contains_duplicate(nums)  # 实际调用函数
        assert result is expected  # assert：检查结果符合预期
        print(nums, "->", result)  # 显示本组结果

"""1480：一维数组的动态和，2026-10-19 复习整理版。

循环版用于练习；NumPy 版用于对照。原始练习过程保存在 d8/practice.ipynb。
"""

import numpy as np  # 导入 NumPy，简写成 np


def running_sum(nums):  # 接收数字列表，返回每个位置的累计和
    total = 0  # 当前累计和：只在循环开始前初始化一次
    result = []  # 用来保存每一步的累计结果

    for x in nums:  # 按顺序读取每个数字
        total += x  # 将当前数字加进累计和，等价于 total = total + x
        result.append(total)  # append：把累计和追加到列表末尾

    return result  # 所有数字处理完后返回；位于函数内、循环外


def running_sum_numpy(nums):  # 使用 NumPy 完成同样的累计计算
    numbers = np.array(nums, dtype=np.int64)  # 转成 64 位整数数组
    cumulative = np.cumsum(numbers)  # cumsum：计算每个位置的累计和
    return cumulative.tolist()  # tolist：转回普通 Python 列表后返回


if __name__ == "__main__":  # 直接运行这个文件时，执行下面的检查
    examples = [  # 每一组分别保存输入列表和预期结果
        ([2, 5, -1, 4], [2, 7, 6, 10]),
        ([3], [3]),
        ([0, 0, 0], [0, 0, 0]),
        ([-2, -1, 3], [-2, -3, 0]),
    ]

    for nums, expected in examples:  # 分别取出输入 nums 和预期结果 expected
        loop_result = running_sum(nums)  # 实际调用循环版
        numpy_result = running_sum_numpy(nums)  # 实际调用 NumPy 版
        assert loop_result == expected  # assert：检查循环版结果符合预期
        assert numpy_result == expected  # 检查 NumPy 版结果符合预期
        print("输入：", nums)  # 显示本组输入
        print("循环版：", loop_result)  # 显示循环版结果
        print("NumPy版：", numpy_result)  # 显示 NumPy 版结果

    print("四组输入的两种实现均通过检查。")  # 全部检查通过后显示

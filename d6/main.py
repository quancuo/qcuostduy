import numpy as np

# 第一个维度：天，共 5 天
# 第二个维度：主题，共 3 个
# 列顺序：Python、Git、数学
# 预计 shape：(5, 3)
minutes = np.array([
    [20,45,30],
    [35,20,50],
    [60,30,25],
    [15,40,45],
    [30,55,20],
], dtype=np.int64)

print(minutes)

print("shape =", minutes.shape)
print("size =", minutes.size)
print("ndim =", minutes.ndim)
print("itemsize =", minutes.itemsize)
print("dtype =", minutes.dtype)

#day2
day2= minutes[1,:]
print("day2 =", day2)
print("day2 shape =", day2.shape)

##区别在于是否保留二维数组的形式，day2是一个一维数组，而day2_table是一个二维数组
##结果上看多一个[],,,,,shape can see the difference
day2_table = minutes[1:2,:]
print("day2_table =", day2_table)
print("day2_table shape =", day2_table.shape)

#python 5days date
python_5days = minutes[:,0]
print("python_5days =", python_5days)
print("python_5days shape =", python_5days.shape)

python_5days_table = minutes[:,0:1]
print("python_5days_table =", python_5days_table)  
print("python_5days_table shape =", python_5days_table.shape)


part = minutes[1:4,0:2]
print("part =", part)
print("part shape =", part.shape)

##output type===true or false

##先标记出来元素结果true or false，，，，然后调用其所在的位置，输出其所在位置的元素
mask = minutes > 30
print("mask =", mask)
print("mask shape =", mask.shape)

over30 = minutes[mask]
##over30= minutes[minutes>30]  等效调用
print("over30 =", over30)
print("shape =",over30.shape)

reshaped = minutes.reshape(3,5)
print("reshaped =", reshaped)
print("reshaped shape =", reshaped.shape)
##本例使用默认顺序，可以理解为：
#1. 按原数组的行顺序依次读取这 15 个数。
#2. 每 5 个数组织成一行。
#3. 最后得到 3 行。
#因此，重新组织后的三行，不能直接解释为三个主题。数据只是按新形状重新分组。
#也可以变成一维：

flat = minutes.reshape(15)
print("flat =", flat)
print("flat shape =", flat.shape)


#转置

transposed = minutes.T
print("transposed =", transposed)
print("transposed shape =", transposed.shape)

# 先复制今天的数字数组，供实验使用
demo = minutes.copy()

# 基本切片得到一个共享 demo 数据的视图
column = demo[:, 0]

column[0] = 999

print("demo 的第一个值 =", demo[0, 0])
print("原始 minutes 的第一个值 =", minutes[0, 0])


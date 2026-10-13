original = [20, 45, 30]

# 赋值：让 shared 也指向原来的列表
shared = original

# 复制：创建一个新的外层列表
copied = original.copy()

print("original is shared =", original is shared)
print("original is copied =", original is copied)
print("original == copied =", original == copied)

# 通过 shared 修改那个共享列表
shared.append(60)

print("original =", original)
print("shared =", shared)
print("copied =", copied)

# 修改副本列表的第一项
copied[0] = 99

print("修改副本后 original =", original)
print("修改副本后 copied =", copied)

# 让 shared 指向另一个新列表
shared = [1, 2]

print("重新赋值后 original =", original)
print("重新赋值后 shared =", shared)
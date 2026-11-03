# D15：复做 LeetCode 20「有效的括号」。本文件与原有 cs61A/20.py 分开保存。
# 栈（stack）：后进先出；下面把列表右侧作为栈顶。
# 函数的输入约定：字符串只含英文括号 ()[]{}，与原题的字符范围一致。


def is_valid(s):  # 定义判断函数；s 是需要检查的括号字符串。
    pairs = {  # 创建字典：用右括号查找它应匹配的左括号。
        ")": "(",  # 右圆括号应匹配左圆括号。
        "]": "[",  # 右方括号应匹配左方括号。
        "}": "{",  # 右花括号应匹配左花括号。
    }
    stack = []  # 创建空列表，保存尚未匹配的左括号。

    for char in s:  # 从左到右，每次取出一个字符，临时命名为 char。
        if char in "([{":  # 如果当前字符是三种左括号之一。
            stack.append(char)  # 把左括号加入列表末尾，也就是压入栈顶。
        else:  # 按本函数的输入约定，剩余字符都是右括号。
            if not stack:  # 如果列表为空，就没有左括号能与当前右括号配对。
                return False  # 立即结束整个函数，判断为无效。
            if stack[-1] != pairs[char]:  # 先查看栈顶；它必须是当前右括号所需的左括号。
                return False  # 类型不匹配，立即结束；此时尚未执行 pop，栈保持原样。
            stack.pop()  # 已确认匹配，移除栈顶左括号；这对括号就处理完了。

    return not stack  # 全部字符检查后，空栈返回 True；仍有左括号则返回 False。


if __name__ == "__main__":  # 直接运行本文件时才执行下面的核对；导入函数时不自动核对。
    assert is_valid("()") is True  # 一对圆括号可以匹配。
    assert is_valid("()[]{}") is True  # 三对括号依次匹配。
    assert is_valid("([])") is True  # 先关方括号，再关外层圆括号。
    assert is_valid("([{}])") is True  # 三种括号嵌套，关闭顺序与打开顺序相反。
    assert is_valid("{[()]}") is True  # 换一种嵌套顺序，仍应匹配。
    assert is_valid("((()))") is True  # 相同类型的多层嵌套也应匹配。
    assert is_valid("([)]") is False  # 错序：读到 ) 时栈顶为 [，不能匹配。
    assert is_valid("(]") is False  # 类型不匹配：圆括号不能与方括号配对。
    assert is_valid("(()") is False  # 缺少一个右括号，循环结束后栈非空。
    assert is_valid("((") is False  # 只有左括号，循环结束后栈非空。
    assert is_valid(")(") is False  # 开头就是右括号；空栈不能完成匹配。
    assert is_valid(")") is False  # 只有右括号，也应在空栈处提前返回。
    assert is_valid("())") is False  # 前两个字符匹配后，额外的右括号遇到空栈。
    assert is_valid("][") is False  # 数量相等也可能无效：关闭括号不能先于打开括号。
    assert is_valid("") is True  # 本地扩展：空串没有未匹配括号；不是原题非空输入要求中的必测项。
    print("D15 有效括号复做：15 组核对全部通过。")  # 能运行到这里，表示上面的 15 个 assert 均通过。

# 时间复杂度 O(n)：n 是字符串长度，每个字符至多检查一次、压栈一次、出栈一次。
# 额外空间复杂度 O(n)：最坏情况下全部都是左括号，栈中会保存 n 个字符。
# pairs 只有三个固定配对，其占用空间不随 n 增加，不改变 O(n) 的结论。

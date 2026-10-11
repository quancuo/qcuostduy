返回前：
Global：value = 100，add_one 指向函数对象
f1：value = 4，answer = 5，parent = Global
result 尚未绑定

返回后：
Global：value = 100，result = 5，add_one 指向函数对象
f1 的本次调用已经结束返回前：
Global：value = 100，add_one 指向函数对象
f1：value = 4，answer = 5，parent = Global
result 尚未绑定

返回后：
Global：value = 100，result = 5，add_one 指向函数对象
f1 的本次调用已经结束
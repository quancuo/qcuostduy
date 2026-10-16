from study_record import StudyRecord


python_record = StudyRecord("Python")
python_record.add_session(30)
python_record.add_session(45)

git_record = StudyRecord("Git")
git_record.add_session(20)

# 判断两个对象及其内部列表是否相同
print("两个对象相同 =", python_record is git_record)
print("两个时长列表相同 =", python_record.sessions is git_record.sessions)

# alias：别名，让另一个名字指向 Python 对象
alias = python_record

print("alias 与 python_record 相同 =", alias is python_record)

# 通过别名修改同一个对象
alias.add_session(15)
alias.topic = "Python 基础"

print("Python 主题 =", python_record.topic)
print("Python 时长记录 =", python_record.sessions)
print("Python 总时长 =", python_record.total_minutes())

print("Git 时长记录 =", git_record.sessions)
print("Git 总时长 =", git_record.total_minutes())
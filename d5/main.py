from study_record import StudyRecord


def main():
    # 创建 Python 主题的学习记录对象
    python_record = StudyRecord("Python")

    python_record.add_session(30)
    python_record.add_session(45)

    file_record = StudyRecord("File Handling")
#检查
    print("初始总时长 =", file_record.total_minutes())
    file_record.add_session(25)
    file_record.add_session(35)
    print("File Handling 主题 =", file_record.topic)
    print("File Handling 时长记录 =", file_record.sessions)
    print("File Handling 总时长 =", file_record.total_minutes())


    # 创建 Git 主题的另一个学习记录对象
    git_record = StudyRecord("Git")

    git_record.add_session(20)

    print("Python 主题 =", python_record.topic)
    print("Python 时长记录 =", python_record.sessions)
    print("Python 总时长 =", python_record.total_minutes())

    print("Git 主题 =", git_record.topic)
    print("Git 时长记录 =", git_record.sessions)
    print("Git 总时长 =", git_record.total_minutes())

    total = python_record.total_minutes() + git_record.total_minutes()+ file_record.total_minutes()

    print("全部学习时长 =", total)
    print("时长单位 =", StudyRecord.unit)


    empty_record = StudyRecord("尚未开始")
    print("空记录的学习次数 =", empty_record.session_count())
    print("Python 学习次数 =", python_record.session_count())
    print("Git 学习次数 =", git_record.session_count())

if __name__ == "__main__":
    main()
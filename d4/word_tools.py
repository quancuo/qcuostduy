def read_text(file_path):
    # read_text：读取文本
    # file_path：文件路径
    with open(file_path, "r", encoding="utf-8") as text_file:
        # text_file：已经打开的文本文件对象
        # read()：读取文件的全部内容，得到字符串
        text = text_file.read()

    return text


def count_words(text):
    # lower()：把英文转换为小写
    # split()：按空白拆分，得到单词列表
    words = text.lower().split()

    counts = {}

    for word in words:
        if word in counts:
            counts[word] = counts[word] + 1
        else:
            counts[word] = 1

    return counts



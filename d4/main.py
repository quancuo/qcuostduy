from pathlib import Path
from word_tools import read_text, count_words


def main():
    # 找到 main.py 所在的文件夹
    folder = Path(__file__).resolve().parent

    # 拼接出同一文件夹中 input.txt 的完整路径
    file_path = folder / "input.txt"

    try:
        text = read_text(file_path)
    except FileNotFoundError:
        print("找不到文件：", file_path)
        print("请确认 input.txt 位于 main.py 同一文件夹中。")
        return

    counts = count_words(text)

    print("读取文件：", file_path)
    print("词频结果：", counts)
    print("不同单词数：", len(counts))


if __name__ == "__main__":
    main()

print("大小写测试 =", count_words("Python PYTHON python"))
print("空白测试 =", count_words("git    git\npython"))
print("空文本测试 =", count_words(""))
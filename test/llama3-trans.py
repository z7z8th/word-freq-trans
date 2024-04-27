import sys

import re
from collections import Counter
import requests
import openai

 # 读取txt文件
def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    return text

  # 统计单词频率
def count_words(text):
    words = re.findall(r'\b\w+\b', text)
    word_freq = Counter(words)
    return word_freq

  # 翻译单词使用 OpenAI API
def translate_word(word, lang='zh'):
    OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY'
    message = [
            {
                "role": "system",
                "content": "你是一个翻译助手，请把所有输入翻译成中文，不是拼音，不要出现emoji"
            },
            {
                "role": "user",
                "content": word
            }
        ]

    client = openai.Client(base_url="http://localhost:4891/v1", api_key=OPENAI_API_KEY)  # <--- Change this line!
    response = client.chat.completions.create(
        model='Meta-Llama-3-8B-Instruct.Q4_0.gguf',
        messages = message,
        max_tokens=100,  # adjust this to control the response length
        temperature=0.5,  # adjust this to control the response tone (e.g., more formal or casual),
    )
    translation = response.choices[0].message.content
    return translation

  # 输出结果
def output_results(word_freq):
    for word, freq in sorted(word_freq.items(), key=lambda x: (-x[1], x[0])):
        print(f"{freq} {word} {translate_word(word)}")

  # 主函数
if __name__ == '__main__':
    filename = sys.argv[1] #'book.txt'  # Replace with your file name
    text = read_file(filename)
    word_freq = count_words(text)
    output_results(word_freq)

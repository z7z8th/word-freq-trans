#!/usr/bin/env python

import os
import sys
import time
import re
from collections import Counter
from translate import Translator
import traceback

import argostranslate.package
import argostranslate.translate
import argostranslatefiles
from argostranslatefiles import argostranslatefiles


def get_translator():
  from_code = "en"
  to_code = "zh"

  # Translate
  installed_languages = argostranslate.translate.get_installed_languages()
  from_lang = list(filter(
          lambda x: x.code == from_code,
          installed_languages))[0]
  to_lang = list(filter(
          lambda x: x.code == to_code,
          installed_languages))[0]
  translation = from_lang.get_translation(to_lang)
  return translation
  # translatedText = translation.translate("Hello World!")

#  # 读取txt文件
def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    return text.lower()

  # 统计单词频率
def count_words(text):
    words = re.findall(r"\b[\w'\d]+\b", text)
    word_freq = Counter(words)
    return word_freq

translator = get_translator()

  # 输出结果
def output_results(word_freq):
    for word, freq in sorted(word_freq.items(), key=lambda x: (-x[1], x[0])):
        print(f"{freq} {word} {translator.translate(word)}")
        # time.sleep(1)

  # 主函数
if __name__ == '__main__':
    filename = sys.argv[1] #'book.txt'  # Replace with your file name
    # argostranslatefiles.translate_file(translator, os.path.abspath(filename))
    text = read_file(filename)
    word_freq = count_words(text)
    output_results(word_freq)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import glob
import re
import math
import json
import traceback
from collections import Counter
import odf.opendocument
from pystardict import Dictionary
import datetime

WORD_PER_PAGE = 500

args = None

star_dicts: list[Dictionary] = []

def load_dicts():
    dicts_dir = os.path.join(os.path.dirname(__file__))
    verbose_dict = []
    for d in glob.glob(os.path.join(dicts_dir, '*','*.ifo')):
        dict_base_name = re.sub(r'.ifo$', '', d)
        dict1 = Dictionary(dict_base_name, in_memory=True)
        if '朗道' in dict1.ifo.bookname:  # definition too long, as last choice
            verbose_dict.insert(0, dict1)
        elif '牛津' in dict1.ifo.bookname:  # too verbose
            verbose_dict.append(dict1)
        else:
            star_dicts.insert(0, dict1)  # prefer short definitions

    star_dicts.extend(verbose_dict)
    print(f'{len(star_dicts)} dict(s) loaded', [d.ifo.bookname for  d in star_dicts])

load_dicts()

def max_common_substring_all_concat(s1, s2, max_only = True):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    maxlen = 0
    maxpos = (-1, -1)

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > maxlen:
                    maxlen = dp[i][j]
                    maxpos = (i, j)
            else:
                if max_only:
                    dp[i][j] = 0 # use this to get single mcs only
                else:
                    dp[i][j] = dp[i - 1][j - 1]
    mcs = s1[maxpos[0]-maxlen:maxpos[0]]
    if max_only:
        # print('mcs ', mcs)
        return mcs
    # print("mcs", mcs, ' maxlen ', maxlen, ' maxpos ', maxpos)
    result = ""

    i, j = m, n
    while i > 0 and j > 0:
        if s1[i - 1] == s2[j - 1]:
            result += s1[i - 1]
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    # print(result)
    return result[::-1]

# s1 = "fqwraofabcdefij174509812375908723495087opqxyk;lk;bananalk"
# s2 = "ananaxycdefuvwopquvoipoaisf"

# print(max_common_substring_all_concat(s1, s2, True))

class word_def_cache():
    def __init__(self, fname = None):
        self.cc_file = fname or 'word_def_cache.json'
        try:
            self.load()
        except:
            self.cc = {}

    def load(self):
        with open(self.cc_file, 'r', encoding='utf-8') as f:
            self.cc = json.load(f)

    def save(self):
        with open(self.cc_file, 'w+', encoding='utf-8') as f:
             json.dump(self.cc, f, ensure_ascii=False)

    def add(self, k, v):
        self.cc[k] = v

    def query(self, k):
        if k in self.cc:
            return self.cc[k]

wdcc = word_def_cache()

import multiprocessing
from multiprocessing import Process
from multiprocessing import Value
import queue

def consumer(name, input_queue, output_queue, consumer_exit):

    while not consumer_exit.value:
        try:
            # Consume data from the queue
            word, freq = input_queue.get(block=True, timeout=1)
            # print(f"{name} consumed: {dw, word}")
            wdef = query_dicts(word)
            output_queue.put((word, freq, wdef))
        except queue.Empty:
            # No more items in the queue, exit the loop
            # print('Empty')
            time.sleep(0.1)
        except KeyboardInterrupt:
            # print(f'KeyboardInterrupt in worker {name}')
            output_queue.close()
            input_queue.close()
            return

input_queue = multiprocessing.Queue(1048576)
output_queue = multiprocessing.Queue(1048576)
consumer_exit = Value('b', False)
# Create a list to store threads
consumer_threads: list[Process] = []
def start_consumers():
    # Get the number of CPU cores:
    cpu_count = multiprocessing.cpu_count()
    print('start consumers', cpu_count)
    # cpu_count = 8
    #  Create a queue to hold the data
    # multiprocessing.set_start_method('spawn', force=True)
    for i in range(cpu_count):
        t = Process(target=consumer, args=(i, input_queue, output_queue, consumer_exit))
        t.start()
        consumer_threads.append(t)


#  Wait for all consumer_threads to finish
def shutdown_consumers():
    print('shutdown_consumers')
    wdcc.save()
    consumer_exit.value = True
    # time.sleep(2)
    for t in consumer_threads:
        # print('joining', t.pid)
        t.join()

    # input_queue.close()
    # output_queue.close()

    print('shutdown_consumers done')

def query_dicts_ambiguously(word):
    print('Ambiguously querying', word)
    start_time = time.time()
    maxn = 0
    maxdw = ''
    maxmcs = ''
    for d in star_dicts:
        for dw in d.idx.keys():
            if ' ' in dw:
                continue
            rmcs = max_common_substring_all_concat(dw, word, True)
            if len(rmcs) > maxn:
                maxn = len(rmcs)
                maxdw = dw
                maxmcs = rmcs

    print(f"Got '{maxdw}'({maxn}, {maxmcs}) Elapsed time: {(time.time() - start_time)*1000:.2f} ms\n")

    return maxdw, query_dicts(maxdw, True)

query_no_def_count = 0
def query_dicts(word: str, noguess = False):
    global query_no_def_count
    for d in star_dicts:
        if word in d:
            return d[word]

    if noguess:
        return ''

    if word == word.capitalize():
        gdef = query_dicts(word.lower(), True)
        if gdef:
            return f"~= {word.lower()}\n{gdef}"

    suffix = [('ied', 'y'), ('ies', 'y'), ('iest', 'y'), ('est', ''), ('er', ''), ('er', 'e'), ('ed', ''), ('ed', 'e'), ('ing', ''), ('ing', 'e'), ('s', ''), ('es', 'e'), ('es', ''), ("'s", "")]
    for s, r in suffix:
        gword = re.sub(f'{s}$', r, word)
        gdef = query_dicts(gword, True)
        if gdef:
            return f"~= {gword}\n{gdef}"

    gdef = query_dicts(word.capitalize(), True)
    if gdef:
        return f"~= {word.capitalize()}\n{gdef}"

    abbrexpand = [(r"'ll$", " will"), (r"n't$", " not"), (r"'d$", " would"), (r"-+", " ")]
    for s, r in abbrexpand:
        if re.search(s, word):
            return re.sub(s, r, word)

    gdef = query_dicts(word.upper(), True)
    if gdef:
        return f"~= {word.upper()}\n{gdef}"

    gdef = query_dicts(word.lower(), True)
    if gdef:
        return f"~= {word.lower()}\n{gdef}"

    gword, gdef = query_dicts_ambiguously(word)
    if gword:
        return f"~~~= {gword}\n{gdef}"

    print('No def: ', word)
    query_no_def_count = query_no_def_count + 1
    return ' '

def read_txt_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()

    if len(args.pageids) == 0:
        return text
    words = re.split(r'\s+', text)
    npages = math.ceil(len(words)/WORD_PER_PAGE)
    print('npages', npages)
    pages = []
    for i in args.pageids:
        if i <= npages:
            print('reading page', i)
            pages.extend(words[(i-1)*WORD_PER_PAGE : i*WORD_PER_PAGE])
    return ' '.join(pages)

import PyPDF2
def read_pdf_file(filename):
    # creating a pdf reader object
    reader = PyPDF2.PdfReader(filename)

    # print the number of pages in pdf file
    npages = len(reader.pages)
    print('pdf total pages', npages)

    text = []
    if len(args.pageids) > 0:
        for i in args.pageids:
            if i <= npages:
                print('reading page', i-1)
                text.append(reader.pages[i-1].extract_text())
    else:
        text = [ reader.pages[i].extract_text() for i in range(npages) ]

    ret = ''.join(text)
    # print('ret', ret)
    return ret

import srt

def time_to_delta(x):
    return datetime.timedelta(hours=x.hour, minutes=x.minute, seconds=x.second, microseconds=x.microsecond)

def read_srt_file(filename, ret_obj=False):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()

    # subs is a generator
    subs = srt.parse(text)

    if len(args.time_range) == 0:
        print('use whole srt file')
        if ret_obj:
            # make a copy
            return [ x for x in subs]
        else:
            return text

    for i,t in enumerate(args.time_range):
        args.time_range[i] = time_to_delta(t)

    [start, end] = args.time_range
    print(f'time range {start} - {end}')

    sub_part = []
    text = ''
    for s in subs:
        if s.start > start and s.start < end:
            sub_part.append(s)
            text += s.content
        if s.start > end:
            break

    if ret_obj:
        return  sub_part
    else:
        return text

  # 读取txt文件
def read_file(filename: str):
    readers = {
        'txt': read_txt_file,
        'pdf': read_pdf_file,
        'srt': read_srt_file,
    }

    _, ext = os.path.splitext(filename)
    ft = ext and ext[1:] or 'txt'
    if ft not in readers:
        ft = 'txt'
    text = readers[ft](filename)
    return text and text.lower()


  # 统计单词频率
def count_words(text: str):
    words = re.findall(r'\b[\w\'-]+\b', text)
    words2 = []
    for w in words:
        w = re.sub(r'^\d+|\d+$', '', w)
        w and words2.append(w)
    word_freq = Counter(words2)
    return word_freq

def format_def(wdef: str):
    return wdef and re.sub(r'([a-zA-Z]+\.)[\r\n]+', r'\1 ', wdef)

def get_word_defs(word_freq:Counter, close_queue=True):
    wdeflist = []
    qcnt = 0
    for word, freq in word_freq.most_common():
        if re.match(r'^\s*(\d+|\w)\s*$', word):
            continue
        wdef = wdcc.query(word)
        if not wdef:
            input_queue.put((word, freq))
            qcnt += 1
        else:
            wdeflist.append((word, freq, wdef))
        # if qcnt > 100: break

    i = 0
    while i < qcnt:
        try:
            word, freq, wdef = output_queue.get(block=True, timeout=1)
            i += 1
            wdef = format_def(wdef) or f'No definition found for {word}'
            wdcc.add(word, wdef)
            wdeflist.append((word, freq, wdef))
        except queue.Empty:
            time.sleep(0.1)

    if close_queue:
        input_queue.close()
        output_queue.close()
    return wdeflist
  # 输出结果

def word_defs_to_text(wdeflist):
    text = ''
    for word, freq, wdef in wdeflist:
        wdef = wdef.replace('\n', '; ')
        text += f'\n<b>{word}</b> : {wdef}\n'
    return text

def proc_word_defs_subs(subs, bookname):
    for s in subs:
        # print('s', s.content)
        word_freq = count_words(s.content)
        wdefl = get_word_defs(word_freq, False)

        s.content = f'<font color="yellow">{s.content}</font>\n<font size="40px">{word_defs_to_text(wdefl)}</font>'

    bookname += '.srt'
    with open(bookname, 'w+', encoding='utf-8') as f:
        txt = srt.compose(subs)
        f.write(txt)
        print('result written to', bookname)


# import openpyxl

# def output_results_xlsx(word_freq):
#     # Create a new workbook:
#     wb = openpyxl.Workbook()
#     ws = wb.active  # Get the active worksheet

#     # Set the cell value with multi-line content:
#     cell_value = "Line 1\nLine 2\nLine 3"
#     ws['A1'] = cell_value

#     # Save the file:

#     i=1
#     for word, freq in sorted(word_freq.items(), key=lambda x: (-x[1], x[0])):
#         wdef =  query_dicts(word) or f'No definition found for {word}'
#         # print(f"{freq} {word} {wdef.strip()}")
#         ws[f'A{i}'] = freq
#         ws[f'B{i}'] = word
#         ws[f'C{i}'] = wdef
#         i=i+1
#         # break
#     wb.save('example.xlsx')

from odf.opendocument import OpenDocumentSpreadsheet
from odf.style import (ParagraphProperties, Style, TableColumnProperties, TableCellProperties,
                       TextProperties)
from odf.table import Table, TableCell, TableColumn, TableRow
from odf.text import P, Span

def output_results_odf(word_freq, bookname):

    textdoc = OpenDocumentSpreadsheet()

    # Create automatic styles for the column widths.
    # We want two different widths, one in inches, the other one in metric.
    # ODF Standard section 15.9.1
    widthshort = Style(parent=textdoc.automaticstyles,
                    name='Wshort', family='table-column')
    TableColumnProperties(parent=widthshort, columnwidth='1.3cm')  #

    widthmid = Style(parent=textdoc.automaticstyles,
                    name='Wmid', family='table-column')
    TableColumnProperties(parent=widthmid, columnwidth='3cm')  #

    widthwide = Style(parent=textdoc.automaticstyles,
                    name='Wwide', family='table-column')
    TableColumnProperties(parent=widthwide, columnwidth='12cm')

    # table title cell
    titlecell = Style(parent=textdoc.automaticstyles, name = 'titlecell', family='table-cell')
    TableCellProperties(parent=titlecell, textalignsource='fix', verticalalign='middle')
    ParagraphProperties(parent=titlecell, textalign='center')
    TextProperties(parent=titlecell, fontweight='bold', fontweightasian='bold', fontweightcomplex="bold", fontsize='18pt', fontsizeasian='18pt', fontsizecomplex='18pt')

    # table head cell
    theadcell = Style(parent=textdoc.automaticstyles,
                    name='Theadcell', family='table-cell')
    TableCellProperties(parent=theadcell, textalignsource='fix', verticalalign='middle')
    ParagraphProperties(parent=theadcell, textalign='center')
    TextProperties(parent=theadcell, fontweight='bold', fontweightasian='bold', fontweightcomplex="bold", fontsize='14pt', fontsizeasian='14pt', fontsizecomplex='14pt')

    # table freq cell
    tcell = Style(parent=textdoc.automaticstyles,
                    name='Tcell', family='table-cell')
    TableCellProperties(parent=tcell, textalignsource='fix', verticalalign='middle', wrapoption="wrap")
    ParagraphProperties(parent=tcell, textalign='center')
    TextProperties(parent=tcell, fontsize='12pt')

    # table word cell
    twordcell = Style(parent=textdoc.automaticstyles,
                    name='Twordcell', family='table-cell')
    TableCellProperties(parent=twordcell, textalignsource='fix', verticalalign='middle', wrapoption="wrap")
    ParagraphProperties(parent=twordcell, textalign='center')
    TextProperties(parent=twordcell, fontweight='bold', fontsize='12pt')

    # table def cell
    tdefcell = Style(parent=textdoc.automaticstyles,
                    name='Tdefcell', family='table-cell')
    TableCellProperties(parent=tdefcell, textalignsource='fix', verticalalign='middle', padding='0.15cm', wrapoption="wrap")
    ParagraphProperties(parent=tdefcell, textalign='left')
    TextProperties(parent=tdefcell, fontsize='12pt')

    # Start the table, and describe the columns
    table = Table(parent=textdoc.spreadsheet, name='Word frequency and definitions')
    TableColumn(parent=table, numbercolumnsrepeated=1, stylename=widthshort, defaultcellstylename = tcell)
    TableColumn(parent=table, numbercolumnsrepeated=1, stylename=widthmid, defaultcellstylename = twordcell)
    TableColumn(parent=table, numbercolumnsrepeated=1, stylename=widthwide, defaultcellstylename = tdefcell)

    # book name row, 3 columns
    tr = TableRow(parent=table)
    tc = TableCell(parent=tr, stylename = titlecell, numbercolumnsspanned="3")
    P(parent=tc, text=bookname)

    # head name row
    tr = TableRow(parent=table)
    for txt in ['Freq', 'Word', 'Definition']:
        tc = TableCell(parent=tr, stylename = theadcell)
        P(parent=tc, text=txt)

    n=0
    for word, freq, wdef in sorted(word_freq, key=lambda x: (-x[1], x[0])):
        # print(f"{freq} {word} {wdef.strip()}")
        tr = TableRow(parent=table)
        for txt in [freq, word, wdef]:
            tc = TableCell(parent=tr)
            P(parent=tc, text=txt)
        n = n+1
        # if i>10: break
    ofile = f'{bookname}.ods'
    textdoc.save(ofile)
    print(f'total {n} words')
    print(f"word freq and defs outputed to '{ofile}'")

# query_dicts("that'll")


import argparse
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action='store_true', help="increase output verbosity")
    parser.add_argument("-p", "--pages", help="page range, e.g. 1,2,5,9-12,20")
    parser.add_argument("-t", "--time", help="time range, e.g. 00:00:00-00:10:00")
    parser.add_argument("-c", "--combine", action='store_true', help="combine definition with srt content")
    parser.add_argument("files", nargs="+", help="input files")
    args = parser.parse_args()

    if args.verbose:
        print("Verbose mode enabled!")

    args.pageids = []
    if args.pages:
        for rg in args.pages.split(','):
            prange = rg.split("-")
            print('page range', prange)
            if len(prange) == 1:
                args.pageids.append(int(prange[0]))
            else:
                args.pageids.extend([ i for i in range(int(prange[0]), int(prange[1])+1) ])
        args.pageids = set(args.pageids)
    print('page ids', args.pageids)

    args.time_range = []
    if args.time:
        rg = args.time.split('-')
        if len(rg) != 2:
            raise Exception(f'time range is not correct {args.time}')
        for i,t in enumerate(rg):
            args.time_range.append(datetime.time.fromisoformat(t))

        print('time_range', [ x.isoformat() for x in args.time_range ])

    print('input files', args.files)
    return args


# 主函数
if __name__ == '__main__':
    exit_code = 0
    try:
        args = parse_args()
        start_consumers()
        for filename in args.files:
            # filename = len(sys.argv) > 1 and sys.argv[1] or 'daniel-defoe_robinson-crusoe.pdf'  #'book.txt'  # Replace with your file name
            bookname, _ = os.path.splitext(os.path.basename(filename))
            bookname = re.sub(r'[-.]', ' ', bookname)
            bookname = re.sub(r'[_]', ' - ', bookname)

            if args.combine and filename.endswith('.srt'):
                bookname += ' - defs'
                if args.time:
                    bookname += ' - ' + args.time.replace(':', '_')
                sub_part = read_srt_file(filename, True)
                proc_word_defs_subs(sub_part, bookname)
            else:
                if args.pages:
                    bookname += ' - ' + args.pages

                text = read_file(filename)
                word_freq = count_words(text)

                output_results_odf(get_word_defs(word_freq), bookname=bookname.title())
                print('query_no_def_count', query_no_def_count)
    except KeyboardInterrupt:
        exit_code = -2
    except Exception as e:
        print(e, traceback.format_exc())
    finally:
        shutdown_consumers()
        os._exit(exit_code)

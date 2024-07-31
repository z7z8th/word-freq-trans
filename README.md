# Get word definition for English learning

Output word frequency along with word definition

## Supported input file types

* .txt
* .pdf
* .srt

## Output file types

* .ods
* .srt (Note: Only if input is .srt and option `-c` is used, Use VLC to play the generated .srt)

## Usage

```sh
apt install pipenv
pipenv run bash
pip install -r requirements.txt
```

```sh
3 dict(s) loaded ['懒虫简明英汉词典', '朗道英汉字典5.0', '牛津英汉双解美化版']
usage: word-freq-trans.py [-h] [-v] [-p PAGES] [-t TIME]
                          [-o OUTPUT] [-c]
                          files [files ...]

positional arguments:
  files                 input files

options:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -p PAGES, --pages PAGES
                        page range, e.g. 1,2,5,9-12,20
  -t TIME, --time TIME  srt subs time range, e.g. 00:00:00-00:10:00
  -o OUTPUT, --output OUTPUT
                        output to file
  -c, --combine         combine definition with srt content
```

## Screenshots

![word def ods](image/word-def-ods.png)
![word def srt](image/word-def-srt.png)

# coding: utf-8
#
# [problem]
# ZipInfo class holds filename as bytes. this causes mojibake for zip has sjis
# encoded string. 2nd byte position of dame-moji is normalized from \ to /
# incorrectly.
#
# [solution]
# this module intercept assignment to hold filename as unicode and handle zip
# better.
#
# [問題]
# ZipInfoクラスはファイル名をバイトで保持するが、ファイル名がsjisの場合に
# 2バイト目のバックスラッシュがパスの正規化でスラッシュに誤って変換されて
# てしまう。これにより解凍時に本来のアーカイブの内容と異なるフォルダが展開
# される。
# [解決]
# いくつかの関数を上書きすることでファイル名をunicodeで扱い文字化けを防ぐ。


# extended zipfile module to handle sjis damemoji well.
from zipfile import *

def cp932_invert(cp932_path):
   from string import printable
   def fun(i):
       pred = i > 0 and cp932_path[i] == '/' and cp932_path[i-1] not in printable
       return '\\' if pred else cp932_path[i]
   lst = map(fun, range(len(cp932_path)))
   uni = ''.join(lst).decode('cp932').replace('\\', '/')
   return uni

def as_unicode_path(path):
   if type(path) is unicode:
       return path

   for enc in ['utf-8', 'sjis', 'cp932', 'euc-jp', 'iso-2022-jp']:
       try:
           return path.decode(enc)
       except:
           pass

   # assume cp932 encoding including dame-moji
   try:
       return cp932_invert(path)
   except:
       return path

def __setattr__(self, name, value):
    if name == 'filename':
        value = as_unicode_path(value)
    object.__setattr__(self, name, value)

ZipInfo.__setattr__ = __setattr__

def infolist(self):
    return filter(lambda info: info.filename[-1] != '/', self.filelist)
ZipFile.infolist = infolist

def namelist(self):
    return map(lambda info: info.filename, self.infolist())
ZipFile.namelist = namelist

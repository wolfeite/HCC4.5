# Author: 骆琦（wolfeite）
# Corp: 朗迹
# StartTime:2020.5.28
# Version:1.0 路径，文件读取处理
import sys
import os
import datetime
import random

class Path():
    def __init__(self, dir=""):
        self.url = False
        self.sep = os.sep
        self.set_path_root()
        self.dir = dir
    def set_path_root(self):
        pathArr = os.path.abspath(sys.argv[0]).split(self.sep)
        self.enter = pathArr.pop()
        self.root = self.sep.join(pathArr)
        self.frozen = getattr(sys, "frozen", False)
        print("Path对象路径分析：入口文件{0}，项目根路径：{1}，frozen：{2}".format(self.enter, self.root, self.frozen))
        if self.frozen:
            print(sys._MEIPASS)

    def __getitem__(self, item):
        '''内置方法, 当使用obj['name']的形式的时候, 将调用这个方法, 这里返回的结果就是值'''
        return getattr(self, item)

    @property
    def dir(self):
        return self.path

    @dir.setter
    def dir(self, dirName):
        self.set_dir(dirName)

    def set_dir(self, dir, root=None):
        print("set_dir>>>", dir, isinstance(dir, (list, tuple)))
        # self.path = self.merge(root or self.root, *dir) if isinstance(dir, (list, tuple)) else self.merge(
        #     root or self.root, dir)
        path = self.merge(root or self.root, *dir) if isinstance(dir, (list, tuple)) else self.merge(
            root or self.root, dir)
        if os.path.isfile(path):
            self.url = path
            paths = path.split(self.sep)
            paths.pop(len(paths) - 1)
            self.path = self.sep.join(paths)
        else:
            self.path = path

    def merge(self, *args):
        print("merge>>>>>", args)
        return self.sep.join(args)

    @classmethod
    def join(cls, *args):
        # 注意加入self.sep将会重置路径
        return os.path.join(*args)

class File():
    upPaths = {}
    def __init__(self, baseDir=""):
        self.path = Path(baseDir)
        if self.path.url:
            self.open(self.path.url)

    @property
    def dir(self):
        return self.path.dir

    @classmethod
    def sizeConvert(cls, size):  # 单位换算
        K, M, G = 1024, 1024 ** 2, 1024 ** 3  # Bytes
        if size >= G:
            return str(round(size / G, 3)) + 'GB'
        elif size >= M:
            return str(round(size / M, 3)) + 'MB'
        elif size >= K:
            return str(round(size / K, 3)) + 'KB'
        else:
            return str(round(size, 3)) + 'B'

    @classmethod
    def timeConvert(cls, size, ch=False):  # 单位换算
        M, H = 60, 60 ** 2
        hour = int(size / H)
        mine = int(size % H / M)
        second = int(size % H % M)
        if not ch:
            return ":".join([hour, mine, second])

        if size < M:
            return str(size) + u'秒'
        if size < H:
            return u'%s分钟%s秒' % (int(size / M), int(size % M))
        else:
            tim_srt = u'%s小时%s分钟%s秒' % (hour, mine, second)
            return tim_srt

    def size(self, fileName, byte=True):
        file = fileName
        if isinstance(file, (list, tuple)):
            file = self.path.join(*fileName)
        file_byte = os.path.getsize(self.path.join(self.dir, file))
        return file_byte if byte else self.sizeConvert(file_byte)

    def file_path(self, fileName):
        url = fileName if os.path.isfile(fileName) else os.path.join(self.dir, fileName)
        self.url = url if os.path.isfile(url) else False
        return self.url

    def named(self, type):
        type = type if type.startswith(".") else "." + type
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(0, 999)) + type

    def outPath(self, src_dir, tar_dir):
        tar_dir = src_dir if not tar_dir else os.path.join(src_dir, tar_dir)
        path = os.path.join(self.dir, tar_dir)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def open(self, fileName, encoding="utf-8", newline=False, lines=True):
        url = self.file_path(fileName)
        if url:
            with open(url, "r", encoding=encoding, errors='ignore') as f:
                # res = f.readlines()#带有\n
                res = f.read().splitlines(newline) if lines else f.read()
            return res

    def write(self, fileName, result=None, type="w", encoding="utf-8", **kwargs):
        url = os.path.join(self.dir, fileName)
        edits = list(result) if isinstance(result, (list, dict, tuple)) else result
        lines = True if isinstance(edits, list) else False
        if not result == None:
            # with open(url, "w", encoding='utf-8',newline='\n') as f:
            with open(url, type, encoding=encoding, **kwargs) as f:
                f.writelines(edits) if lines else f.write(edits)

    def remove(self, dir, fileName):
        path = os.path.join(self.dir, dir, fileName)
        os.path.exists(path) and os.remove(path)

    def removes(self, dir, arrs):
        for fileName in arrs:
            self.remove(dir, fileName)

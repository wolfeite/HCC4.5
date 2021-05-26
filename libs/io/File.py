# Author: 骆琦（wolfeite）
# Corp: 朗迹
# StartTime:2020.5.28
# Version:1.0 路径，文件读取处理
import sys
import os
import datetime
import random, hashlib
from libs.util import Path

class File():
    upPaths = {}
    def __init__(self, baseDir=""):
        self.path, self.result = Path(baseDir), None
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

    @classmethod
    def fastMd5(cls, file_path, piece=256, front_bytes=8):
        # 判断是否同一文件 1：大小相同，2：hash值md5一致
        # 对于上传文件，是否已经存在服务器的思路为：1：客户端使用JS按同样算法获取文件MD5，并上传，2：比较服务启端所拥有文件的MD5值，如果没有相同，则上传，如果有该MD5值，且大小相同，则不上传
        """
            快速计算一个用于区分文件的md5（非全文件计算，是将文件分成s段后，取每段前d字节，合并后计算md5，以加快计算速度）

            Args:file_path: 文件路径,piece: 分割块数,front_bytes: 每块取前多少字节
        """
        size = os.path.getsize(file_path)  # 取文件大小
        block = size // piece  # 每块大小
        h = hashlib.md5()
        # 计算md5
        if size < piece * front_bytes:
            # 小于能分割提取大小的直接计算整个文件md5
            with open(file_path, 'rb') as f:
                h.update(f.read())
                f.seek(0)
        else:
            # 大文件分割计算
            with open(file_path, 'rb') as f:
                index = 0
                for i in range(piece):
                    f.seek(index)
                    h.update(f.read(front_bytes))
                    index += block
                f.seek(0)
        return h.hexdigest()

    @classmethod
    def fileMd5(cls, file, piece=256, front_bytes=8):
        data = file.read()
        size = len(data)  # 取文件大小
        print("上传文件大小为：", size)
        file.seek(0)
        block = size // piece  # 每块大小
        h = hashlib.md5()
        # 计算md5
        if size < piece * front_bytes:
            # 小于能分割提取大小的直接计算整个文件md5
            h.update(data)
        else:
            # 大文件分割计算
            print("大文件读取")
            index = 0
            for i in range(piece):
                file.seek(index)
                h.update(file.read(front_bytes))
                index += block

        file.seek(0)
        return h.hexdigest()

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

    def named(self, type, srcName=""):
        type, timestamp = type if type.startswith(".") else "." + type, datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        srcName = "{0}_".format(srcName) if srcName else ""
        # return datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(0, 999)) + type
        return "{0}{1}_{2}{3}".format(srcName, timestamp, str(random.randint(0, 999)), type)

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

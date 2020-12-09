# Author: 骆琦（wolfeite）
# Corp: 朗迹
# StartTime:2020.5.28
# Version:1.0 打开ini,cfg文件
from configobj import ConfigObj
from .File import File

class Config(File):
    def __init__(self, baseDir):
        super(Config, self).__init__(baseDir)

    @classmethod
    def test_imports(cls):
        print("测试动态加载Config模块成功！")

    def open(self, fileName):
        url = self.file_path(fileName)
        self.result = ConfigObj(url, encoding="UTF8") if url else {}

    def write(self, fileName="", result=None, type="w", encoding="utf-8", **kwargs):
        pass

    def get(self, section, option=None):
        if not option == None and self.has(section, option):
            return self.result[section][option]
        elif option == None and self.has(section):
            return self.result[section]
        else:
            return None

    def set(self, section, res={}):
        con = self.result
        if self.has(section):
            for k, v in res.items():
                con[section][k] = v
        con.write()

    def delete(self, section, option=None):
        if not option == None and self.has(section, option):
            del self.result[section][option]
        elif option == None and self.has(section):
            del self.result[section]
        self.result.write()

    def has(self, section, option=None):
        con = self.result
        sects = con.keys()
        res = False
        if sects.count(section):
            opts, res = con[section].keys(), True
            if not option == None:
                res = True if opts.count(option) else False
        return res

    def refresh(self):
        self.result.reload()

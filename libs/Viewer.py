# Author: 骆琦（wolfeite）
# Corp: 朗迹
# StartTime:2020.6.18
# Version:1.0
from libs.io import Loader
class Requester():
    def __init__(self, request, upPaths=None):
        self.req = request
        if request.method == "GET":
            self.isGet = True
            self.data = self.req.args
        else:
            self.isGet = False
            self.data = self.req.form
        self.files_names = self.getFilesNames()
        self.upPaths = upPaths

    def value(self, key):
        paramVal = self.data.get(key)
        paramVal = self.req.args.get(key) if paramVal == None and not self.isGet else paramVal
        if key in self.files_names:
            paramVal = self.up(key)
        return paramVal

    def up(self, key):
        name = ""
        files = self.req.files
        dataType = files.get(key).mimetype.split("/")  # content_type
        pathType, fileType = dataType[0], dataType[1]
        print("进行参数{0}，的数据{1}上传".format(key, dataType))
        if self.upPaths:
            name = Loader().up(key, self.upPaths)
        else:
            pathType = Loader.upPaths.get(pathType)
            if pathType:
                name = Loader().up(key, pathType)
        return name

    def getFilesNames(self):
        files, names = self.req.files, []
        if len(files) > 0:
            for file in files:
                names.append(file)
        return names

class View():
    def __init__(self, fields, request, **con):
        self.requester = Requester(request, upPaths=con.get("upPaths"))
        self.fields = fields if isinstance(fields, list) else list(fields)
        self.init(con)
        for key in fields:
            setattr(self, key, self.requester.value(key))

    def param(self, name):
        return self.requester.value(name)

    def init(self, con):
        self.config = {"pops": None}
        self.config.update(con)
        pops = self.config["pops"]
        if pops and not isinstance(pops, (list, tuple)):
            self.config["pops"] = (pops,)

    def pops(self, *args):
        for key in args:
            key in self.fields and self.fields.remove(key)

    def keys(self):
        pops = self.config["pops"]
        pops and self.pops(*pops)
        return self.fields

    def get(self, name, defVal=None):
        return getattr(self, name, defVal)

    def __getitem__(self, key):
        '''内置方法, 当使用obj['name']的形式的时候, 将调用这个方法, 这里返回的结果就是值'''
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

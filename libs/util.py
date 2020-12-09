# Author: 骆琦（wolfeite）
# Corp: 朗迹
# StartTime:2020.12.2
# Version:1.0

from libs.Thread import threadFactory
import time
from inspect import isfunction
import os, sys

# 处理路径
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
        self.meipass = getattr(sys, "_MEIPASS", self.root)

    def __getitem__(self, item):
        '''内置方法, 当使用obj['name']的形式的时候, 将调用这个方法, 这里返回的结果就是值'''
        return getattr(self, item)

    @property
    def dir(self):
        return self.path

    @dir.setter
    def dir(self, dirName):
        self.set_dir(dirName)

    def set_dir(self, dir="", root=None):
        dir = dir if isinstance(dir, (list, tuple)) else [dir]
        for i, p in enumerate(["root", "meipass"]):
            attr, base = "path", self.root
            if p == "meipass":
                attr, base = "way", self.meipass
            base = root if root else base
            path = self.merge(base, *dir)

            if os.path.isfile(path):
                self.url = path
                paths = path.split(self.sep)
                paths.pop(len(paths) - 1)
                path = self.sep.join(paths)
            setattr(self, attr, path)
        print("目标：{0}，入口{1}，path：{2}，way：{3}".format(dir, self.enter, self.path, self.way))
    def merge(self, *args):
        return self.sep.join(args)

    @classmethod
    def join(cls, *args):
        # 注意加入self.sep将会重置路径
        return os.path.join(*args)

    def has_files(self, topdown=True, onerror=None, followlinks=False):
        res, rootArr = {}, self.dir.split(self.sep)
        arr_len = len(rootArr)
        for root, dirs, files in os.walk(self.dir, topdown=topdown, onerror=onerror, followlinks=followlinks):
            pathArr = root.split(self.sep)
            _keys = ["top"] if root == self.dir else pathArr[(arr_len):]
            _key = ".".join(_keys)
            res[_key] = {"root": root, "dirs": dirs, "files": files}
        return res

# 插件
class Plug():
    def __init__(self, path, modules=[], exceptions=[]):
        path = path.split(".") if isinstance(path, str) else path
        self.file = Path(path)
        path = path if isinstance(path, (list, tuple)) else [path]
        self.path = ".".join(path)
        self.checkModules(modules, exceptions)

    def checkModules(self, modules=[], exceptions=[]):
        top = self.file.has_files().get("top", {})
        files = top.get("files", [])
        "__init__.py" in files and files.remove("__init__.py")
        files = [os.path.splitext(i)[0] for i in files if os.path.splitext(i)[1] == ".py"]
        modules = modules if modules else files
        self.modules = [m for m in files if m in modules and not m in exceptions]

    @property
    def imports(self):
        return [] if len(self.modules) == 0 else ["{0}.{1}".format(self.path, m) for m in self.modules]

    @classmethod
    def into(cls, path, modules):
        modules = modules if isinstance(modules, (list, tuple)) else []
        if len(modules) == 0:
            print("没有需要导入的插件！")
            return False

        resStr = "from {0} import {1}".format(path, ",".join(modules))
        try:
            exec(resStr)
            print("导入插件", resStr)
        except Exception as e:
            print("插件不存在，导入失败！", resStr)

    def _in_(self):
        self.into(self.path, self.modules)

class PlugIn(Plug):
    def __init__(self, path, modules=[], exceptions=[]):
        super(PlugIn, self).__init__(path, modules=modules, exceptions=exceptions)
        self._in_()

# 字典扁平
def flat_dict(src, sep="."):
    def flat_dict(src, target=None, prefix="", sep="."):
        target = {} if target is None else target
        for k, v in src.items():
            _key = prefix + k
            if isinstance(v, dict):
                flat_dict(v, target, _key + sep)
            else:
                target[_key] = v
        return target
    return flat_dict(src, sep=sep) if isinstance(src, dict) else src

# 装饰器：定时任务
# def setTimeOut(delay=None):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             return func(*args,**kwargs)
#         return wrapper
#     return decorator
def interval(func):
    def wrapper(*args, **kwargs):
        # 配置参数为kwargs中的args,delay
        delay = kwargs.get("delay", None)
        "delay" in kwargs and kwargs.pop("delay")
        if delay == None:
            print("interval中直接执行{0}".format(func.__name__))
            return func(*args, **kwargs)
        else:
            def delayFn(*a, **k):
                arguments = k.get("args", None)
                "args" in k and k.pop("args")
                arguments = arguments if arguments else a
                delays = [delay] if not isinstance(delay, list) else delay
                delays_len, defVal = len(delays), 0.05
                arguments = [arguments] if not isinstance(arguments, (tuple, list)) else arguments
                for i in range(len(arguments)):
                    arg = arguments[i]
                    duration = delays[i] if i < delays_len else defVal
                    print("interval中延迟{0}执行{1}".format(float(duration), func.__name__))
                    time.sleep(float(duration))
                    arg = arg if isinstance(arg, (tuple, list)) else (arg)
                    print(">>>>", *arg)
                    func(*arg, **k)
            return threadFactory(delayFn, args=args, kwargs=kwargs)
    return wrapper

def setTimeOut(func):
    def wrapper(*args, **kwargs):
        # 配置参数为kwargs中的delay
        delay = kwargs.get("delay", None)
        "delay" in kwargs and kwargs.pop("delay")
        if delay == None:
            print("setTimeOut中直接执行{0}".format(func.__name__))
            return func(*args, **kwargs)
        else:
            def delayFn(*a, **k):
                print("setTimeOut中延迟{0}执行{1}".format(float(delay), func.__name__))
                time.sleep(float(delay))
                func(*a, **k)
            return threadFactory(delayFn, args=args, kwargs=kwargs)
    return wrapper

# 间隔时间内只执行数组中某一个指令
class Sets():
    allSets = []
    def __init__(self, orders=[], isSets=True):
        self.sets = orders
        self.mode = "sets" if isSets else "allSets"

    def get(self, name, defVal=None):
        return getattr(self, name, defVal)

    @property
    def orders(self):
        return self.get(self.mode)

    def gap(self, order, delay=None):
        self.push(order, delay=None)
        self.pull(order, delay=delay)

    @setTimeOut
    def push(self, order):
        self.orders.append(order)

    @setTimeOut
    def pull(self, order):
        print("删除将延迟执行，当前为{0},准备删除{1}！".format(self.orders, order))
        self.isHas(order) and getattr(self.orders, "pop" if isinstance(order, int) else "remove")(order)
        print("删除结束，剩余为{0}！".format(self.orders))

    def isHas(self, order):
        return order in self.orders

    def clear(self):
        self.orders.clear()

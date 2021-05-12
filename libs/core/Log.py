# Author: 骆琦（wolfeite）
# Corp: 朗迹
# StartTime:2020.12.18
# Version:1.0
# 日志
'''
日志等级：使用范围

FATAL：致命错误
CRITICAL：特别糟糕的事情，如内存耗尽、磁盘空间为空，一般很少使用
ERROR：发生错误时，如IO操作失败或者连接问题
WARNING：发生很重要的事件，但是并不是错误时，如用户登录密码错误
INFO：处理请求或者状态变化等日常事务
DEBUG：调试过程中使用DEBUG等级，如算法中每个循环的中间状态
'''
import logging, os, datetime
from libs.util import Path

formatter = '[%(asctime)s] [%(levelname)s] [%(process)s->%(thread)s] [%(filename)s->%(lineno)s] [%(message)s]'

def logger(name, path="", flevel=logging.DEBUG):
    # logger = setLogger(name, logging.DEBUG)
    # path and logger.addHandler(setFileHandler(path, flevel))
    # return logger
    logger = Logger.loggers.get(name)
    print("使用现有的logger：", logger and Logger.checkFileHandlers(name, path))
    return logger if logger and Logger.checkFileHandlers(name, path) else Logger(name, path, flevel).logger

def logged(name, path="", flevel=logging.DEBUG):
    logger = Logger.logged.get(name)
    return logger if logger and Logger.checkFileHandlers(name, path) else Logger(name, path, flevel)

def dater(time=""):
    nowDate = datetime.datetime.now().strftime('%Y-%m-%d') if not time else time
    path_data = Path(("data", "log", "{0}.log".format(nowDate)), isFile=True, mk=True)
    return logger("data", path_data.url)
'''
格式测试：
dater().debug("%s -> %s", "jj", "kk")
dater().debug("%(name)s -> %(age)s", {"name": "kdj", "age": 60})
'''
class Logger():
    logged, loggers = {}, {}
    def __init__(self, name="", path="", flevel=logging.DEBUG):
        name = name if name else "root"
        self.logger = self.init_root() if name == "root" else self.init_other(name, path, flevel)
        self.logged[name] = self

    @classmethod
    def checkFileHandlers(cls, name, path):
        logger, res, arr = logging.getLogger(name), False, []
        if not name in ["", "root"] and path:
            arr = [val.baseFilename for i, val in enumerate(logger.handlers) if isinstance(val, logging.FileHandler)]
        return path in arr

    @classmethod
    def init_other(cls, name, path, flevel):
        logger = cls.getLogger(name, logging.DEBUG)
        if path and not logger.handlers:
            cls.addHandler(logger, cls.setFileHandler(path, flevel))
        cls.loggers[name] = logger
        return logger

    @classmethod
    def init_root(cls):
        root_logger, root = cls.getLogger("", logging.DEBUG), cls.loggers.get("root")
        if not root:
            filter, level = logging.Filter(), logging.INFO if Path.frozen and not "debug" in Path.enter else logging.DEBUG
            filter.filter = lambda record: record.levelno >= level
            streamHandler = cls.setStreamHandler(logging.DEBUG)
            streamHandler.addFilter(filter)
            cls.addHandler(root_logger, streamHandler)
            cls.loggers["root"] = root_logger
        return root_logger

    @classmethod
    def getLogger(cls, name="", llevel=logging.DEBUG):
        logger = logging.getLogger(name)
        logger.setLevel(llevel)
        return logger

    @classmethod
    def setStreamHandler(cls, slevel):
        sh = logging.StreamHandler()
        sh.setLevel(slevel)
        sh.setFormatter(logging.Formatter(formatter, '%Y-%m-%d %H:%M:%S'))
        return sh

    @classmethod
    def setFileHandler(cls, path, flevel):
        fh = logging.FileHandler(path)
        fh.setLevel(flevel)
        fh.setFormatter(logging.Formatter(formatter))
        # logger.addHandler(fh)
        return fh

    @classmethod
    def addHandler(cls, logger, handler):
        logger.addHandler(handler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warn(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg, exc_info=True)

    def exception(self, msg):
        self.logger.exception(msg)

    def critical(self, msg):
        self.logger.critical(msg)

Logger()

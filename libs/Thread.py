# Author: 骆琦（wolfeite）
# Corp: 朗迹
# StartTime:2020.5.18
# Version:1.0

import threading
import time
from inspect import isfunction

class Thread(threading.Thread):
    def __init__(self, func, args=[], daemon=True):
        super(Thread, self).__init__(daemon=daemon)
        self.func = func
        self.args = args

    def run(self):
        self.res = self.func(*self.args)

    @property
    def result(self):
        try:
            return self.res
        except Exception:
            return None

def threadFactory(func, args=[], kwargs={}, daemon=True):
    thread = threading.Thread(target=func, args=args, kwargs=kwargs)
    thread.setDaemon(daemon)
    thread.start()
    return thread

class Loop():
    def __init__(self, daemon=True, isClear=True):
        self.interval = 0.1
        self.daemon = daemon
        self.isClear = isClear
        self._pool_ = []
        self._isStop_ = True
        self.begin, self.end = None, None

    def loop(self):
        # 同步加载完轮询池
        time.sleep(0.01)
        isfunction(self.begin) and self.begin()
        print("一个loop进入轮询！！！暂停后是否清空轮询池：{0}，间隔为：{1}，轮询池为：{2}".format(self.isClear, self.interval, self._pool_))
        while not self._isStop_:
            for fns in self._pool_:
                fns[0](*fns[1])
            time.sleep(self.interval)
        isfunction(self.end) and self.end()

    def stop(self):
        self._isStop_ = True
        self._pool_ = [] if self.isClear else self._pool_
        print("一个loop轮询结束！！！暂停后是否清空轮询池：{0}，轮询池为：{1}： <<<".format(self.isClear, self._pool_))
        return self

    def connect(self, func, args=[]):
        fns = (func, args)
        self._pool_.append(fns)
        return self

    def setInterval(self, interval):
        interval = interval / 1000 if isinstance(interval, int) else 0.1
        self.interval = interval

    def start(self, interval=100, begin=None, end=None):
        self.setInterval(interval)
        self.begin, self.end = begin, end
        if self._isStop_:
            self._isStop_ = False
            print(">>>开始创建一个新进程来执行loop!!!")
            threadFactory(self.loop, daemon=self.daemon)

class Timeout(Loop):
    def __init__(self, daemon=True, isClear=True):
        super(Timeout, self).__init__(daemon=daemon, isClear=isClear)

    def loop(self):
        isfunction(self.begin) and self.begin()
        print("timeout类实例！！！暂停后是否清空轮询池：{0}，间隔为：{1}，轮询池为：{2}".format(self.isClear, self.interval, self._pool_))
        p = self._pool_
        length = len(p)
        for i in range(length):
            fns = p[i]
            fns[0](*fns[1])
            i < length - 1 and time.sleep(self.interval)
        isfunction(self.end) and self.end()
        self.stop()

class HeartBeat():
    def __init__(self):
        pass

    def start(self):
        pass

    def keep_alive(self):
        pass

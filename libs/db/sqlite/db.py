# Author: 骆琦（wolfeite）
# Corp: 朗迹
# StartTime:2020.6.10
# Version:1.0：sqlite3通用接口

import sqlite3
from inspect import isfunction
import copy

class SqliteDb():
    def __init__(self, url, **config):
        self.url = url
        self.conf = {}
        self.option = {"cursor": False, "row_factory": False, "dict_factory": True, "cb": None, "format": True,
                       "create_aggregate": None}
        conf = self.setOption(config)
        self.conf.update(conf)
        self.models = {}

    def __getitem__(self, item):
        '''内置方法, 当使用obj['name']的形式的时候, 将调用这个方法, 这里返回的结果就是值'''
        return getattr(self, item)

    def setOption(self, option):
        opt = self.option
        for o in opt:
            val = option.get(o)
            if not val == None:
                opt[o] = val
                option.pop(o)
        return option

    @property
    def connect(self):
        return sqlite3.connect(self.url)

    @connect.setter
    def connect(self, url):
        self.url = url
        return sqlite3.connect(self.url)

    def executor(self, *sql, **option):
        opt = copy.deepcopy(self.option)
        opt.update(option)
        conn = self.connect
        create_aggregate = opt.get("create_aggregate")
        if create_aggregate:
            conn.create_aggregate(*create_aggregate)

        if opt["dict_factory"]:
            conn.row_factory = self.dict_factory
        elif opt["row_factory"]:
            conn.row_factory = sqlite3.Row
        operator = conn.cursor() if opt["cursor"] else conn
        executor = operator.executemany if len(sql) > 1 and isinstance(sql[1], list) else operator.execute
        try:
            with conn:
                print("执行的SQL>>>", *sql)
                sqlStr = sql[0]
                if isinstance(sqlStr, list):
                    for i in sqlStr:
                        result = executor(*i) if isinstance(i, tuple) else executor(i)
                else:
                    result = executor(*sql)
                # result = c.fetchmany(-1)
                result = operator.fetchall() if opt["cursor"] else list(result)
                cb = opt["cb"]
                isfunction(cb) and cb(result)
                return self.format(result, True, "数据库操作成功") if opt["format"] else result
        except sqlite3.IntegrityError as e:
            errorText = "10001-[IntegrityError]{0}".format(e)
            print(errorText)
            if "UNIQUE" in errorText:
                strError = errorText.split(":")
                print(">>>",strError)
                errorText = "10001-[IntegrityError]字段{0}必须唯一".format(strError[1])
            return self.format([], False, errorText) if opt["format"] else errorText
        conn.close()

    def drop(self, name):
        sql = "drop table if exists {0}".format(name)
        self.executor((sql))
        self.unregister(name)
        # c.execute("DROP TABLE IF EXISTS corp2;")

    def register(self, name, items):
        models = self.models
        if name not in models:
            # self.models["name"] = items
            models[name] = Model(self, name, items)
        return models[name]
    def unregister(self, name):
        if name in self.models:
            self.models.pop(name)

    @classmethod
    def dict_factory(cls, cursor, row):
        # print("?>", cursor, row, sd)
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    @classmethod
    def format(cls, result=[], success=True, msg=""):
        return {"success": success, "msg": msg, "data": result}

    @classmethod
    def placeHolder(cls, values):
        holder = ""
        if isinstance(values, tuple):
            holder = ",".join(map(lambda value: "?", values))
        elif isinstance(values, dict):
            holder = ",".join(map(lambda key: ":{0}".format(key), values.keys()))
        elif isinstance(values, list) and len(values) > 0:
            holder = cls.placeHolder(values[0])
        else:
            holder = False
        return holder

    @classmethod
    def clause(cls, cla):
        cla_str = ""
        if isinstance(cla, (list, tuple)):
            cla_str = " ".join(cla)
        elif isinstance(cla, str):
            cla_str = cla
        elif isinstance(cla, dict):
            keys, values = cla.keys(), cla.values()
            cla_str = " ".join(lambda key, val: "{0} {1}".format(key, val), keys, values)
        return cla_str

    def model(self, name, fields, **conf):
        opt = ",".join(map(lambda key, val: " ".join((key, val)), fields.keys(), fields.values()))
        foreign = conf.get("foreign")
        opt = ",".join((opt, foreign)) if foreign else opt
        sql = "create table if not exists {0}({1})".format(name, opt)
        self.executor(sql)
        return self.register(name, fields)
        # c.execute('''
        #     create table if not exists corp(id integer not null primary key autoincrement unique,name text,age int)
        # ''')
    def keys(self, items):
        data = items[0] if isinstance(items, (list, tuple)) else items
        return data.keys()

    def insert(self, table, items, isSql=False, **option):
        # c.execute("insert into corp(name,age) values(?,?)", ("wolfe", 25))
        # c.execute("insert into corp(name,age) values(:caller,:ages)", {"caller": "wolfeite", "ages": 35})
        # field = ",".join(items) if isinstance(items, (list, tuple)) else items
        # holder = self.placeHolder(items)
        keys = self.keys(items)
        fields = ",".join(keys)
        holder = ",".join(map(lambda key: ":{0}".format(key), keys))
        sql = "insert into {0}({1}) values({2});".format(table, fields, holder)
        return sql if isSql else self.executor(sql, items, **option)

    def delete(self, table, clause=None, isSql=False, **option):
        # "DELETE FROM COMPANY WHERE ID = 7;"
        # 删除所有"DELETE FROM COMPANY;"
        sql = "delete from {0} {1}".format(table, self.clause(clause))
        return sql if isSql else self.executor(sql, **option)

    def update(self, table, items, clause=None, isSql=False, **option):
        # "UPDATE COMPANY SET ADDRESS = 'Texas', SALARY = 20000.00 WHERE ID = 6;"
        keys = self.keys(items)
        # set = ",".join(map(lambda key, val: "{0}={1}".format(key, val), keys, values))
        set = ",".join(map(lambda key: "{0}=:{0}".format(key), keys))
        sql = "update {0} set {1} {2};".format(table, set, self.clause(clause))
        return sql if isSql else self.executor(sql, items, **option)

    def find(self, table, items, clause=None, isSql=False, **option):
        items = ",".join(items) if isinstance(items, (list, tuple)) else items
        sql = "select {0} from {1} {2};".format(items, table, self.clause(clause))
        return sql if isSql else self.executor(sql, **option)
        # c.execute("SELECT id, name, address, salary  from COMPANY")
        # cur.execute("SELECT * FROM people WHERE name_last=:who AND age=:age",{"who": who, "age": age})

class Model():
    def __init__(self, db, name, fields):
        self.db = db
        self.name = name
        self.fields = fields
        self.keys = self.fields.keys()

    def insert(self, items, isSql=False, **option):
        return self.db.insert(self.name, items, isSql=isSql, **option)

    def delete(self, clause=None, isSql=False, **option):
        return self.db.delete(self.name, clause=clause, isSql=isSql, **option)

    def update(self, items, clause=None, isSql=False, **option):
        return self.db.update(self.name, items, clause=clause, isSql=isSql, **option)

    def find(self, items, clause=None, isSql=False, **option):
        return self.db.find(self.name, items, clause=clause, isSql=isSql, **option)

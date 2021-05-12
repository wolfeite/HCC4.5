# Author: 骆琦（wolfeite）
# Corp: 朗迹
# StartTime:2020.6.18
# Version:1.0
from libs.analyser.Viewer import View

class ViewModel(View):
    def __init__(self, db, name, request, **con):
        self.model = db.models[name]
        self.byNames = con.get("byNames")
        super(ViewModel, self).__init__(self.model.keys, request, **con)

    def insert(self, row=None, orderBy=None, whereBy=None):
        row = row if row else dict(self)
        for name in list(row.keys()):
            row.get(name) == None and row.pop(name)

        optRes = self.model.insert(row)
        print("optRes:>>", optRes)
        res = self.findBy(self.byNames, orderBy=orderBy, whereBy=whereBy)
        optRes["data"] = res["data"]
        return optRes if not optRes["success"] else res

    def updateById(self, row=None, orderBy=None, whereBy=None):
        row = row if row else dict(self)
        for name in self.requester.files_names:
            not row.get(name) and row.pop(name)
        for name in list(row.keys()):
            row.get(name) == None and row.pop(name)
        optRes = self.model.update(row, clause="where id={0}".format(self.id))
        res = self.findBy(self.byNames, orderBy=orderBy, whereBy=whereBy)
        optRes["data"] = res["data"]
        return optRes if not optRes["success"] else res

    def deleteById(self, foreign_keys=False, orderBy=None, whereBy=None):
        optRes = self.model.delete(clause="where id={0}".format(self.id), isSql=foreign_keys)
        if foreign_keys:
            optRes = self.model.db.executor(["pragma foreign_keys=on;", optRes])
        # optRes = self.model.delete(clause="where id={0}".format(self.id))
        res = self.findBy(self.byNames, orderBy=orderBy, whereBy=whereBy)
        optRes["data"] = res["data"]
        return optRes if not optRes["success"] else res

    def findBy(self, byNames=None, fields="*", orderBy=None, whereBy=None):
        orderBy = orderBy if orderBy else "order by number ASC,id DESC"
        if not orderBy.startswith("where"):
            if whereBy and whereBy.startswith("where"):
                orderBy = "{0} {1}".format(whereBy, orderBy)
            elif byNames and isinstance(byNames, (str, tuple, list)):
                byNames = [byNames] if isinstance(byNames, str) else byNames
                clauseWhere = []
                for name in byNames:
                    val = self.get(name)
                    strCal = "{0}='{1}'" if isinstance(val, str) else "{0}={1}"
                    clauseWhere.append(strCal.format(name, val))
                clause = " and ".join(clauseWhere)
                orderBy = "where {0} {1}".format(clause, orderBy)
        res = self.model.find(fields, clause=orderBy)
        print("findBy{0}>>查询条件：{1}，结果：{2}".format(byNames, orderBy, res))
        return res

    @property
    def pattern(self):
        return self.requester.req.app["pattern"]

    @property
    def mode(self):
        return self.requester.req.app["mode"]

    @property
    def byPatternId(self):
        return self.byPattern()

    def byPattern(self, column="id"):
        pat = self.pattern
        strClause = "{0}>0" if pat == 0 else "{0}=0"
        return strClause.format(column)

    def isPattern(self, val):
        return self.pattern == val

    @property
    def isSingle(self):
        return self.isPattern(self.mode.SINGLE.value)

    @property
    def isMultiple(self):
        return self.isPattern(self.mode.MULTIPLE.value)

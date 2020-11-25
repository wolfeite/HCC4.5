import json
from app.models.Common import factoryDB, getTable, selectTable
from flask import render_template as render, redirect, request
from libs.Viewer import Requester

def getForeign(isDetail=False):
    return selectTable(isDetail).get("foreign", [])

def getTableName(isDetail=False):
    return selectTable(isDetail).get("name")

def getDetailName():
    return selectTable(False).get("detail", {}).get("name")

def getTemplate(path):
    return request.app["template"].get(path, {})

def add_route(bp, **f):
    db = f["db"]

    @bp.route("/", methods=["POST", "GET"])
    def index():
        path = request.path
        path = path if path.endswith("/") else "{0}/".format(path)
        temp = request.app.get("used").get("index")
        temp = "web".format(temp) if temp.startswith("/") else "web/{0}".format(temp)
        # return render_template("web/common/index.html", type="", path=path)
        print("index渲染模板：", temp)
        foreign, tableName, template = getForeign(False), getTableName(False), getTemplate(path)
        isDetail = "detail" in selectTable(False)
        return render(temp, type="", path=path, foreign=foreign, tableName=tableName, template=template,
                      isDetail=isDetail)

    @bp.route("/list", methods=["POST", "GET"])
    def screenList():
        # params = Bigdata(db, request, pops="id")
        params = factoryDB(False, pops="id")
        foreign = getForeign(False)
        return json.dumps(params.findBy(foreign, orderBy="order by number ASC,id DESC"))

    @bp.route("/add", methods=["POST", "GET"])
    def screenAdd():
        # params = Bigdata(db, request, pops="id", byNames="exhibit")
        foreign = getForeign(False)
        params = factoryDB(False, pops="id", byNames=foreign)
        return json.dumps(params.insert(orderBy="order by number ASC,id DESC"))

    @bp.route("/update", methods=["POST", "GET"])
    def screenUpdate():
        # params = Bigdata(db, request, pops="id", byNames="exhibit")
        foreign = getForeign(False)
        params = factoryDB(False, pops="id", byNames=foreign)
        return json.dumps(params.updateById(orderBy="order by number ASC,id DESC"))

    @bp.route("/del", methods=["POST", "GET"])
    def screenDelete():
        # params = Bigdata(db, request, pops="id", byNames="exhibit")
        foreign = getForeign(False)
        params = factoryDB(False, pops="id", byNames=foreign)
        return json.dumps(params.deleteById(orderBy="order by number ASC,id DESC"))

    # 第二层内页
    @bp.route("/detail", methods=["POST", "GET"])
    def index_detail():
        path = request.path
        path = path if path.endswith("/") else "{0}/".format(path)
        params = Requester(request)
        id, name = params.value("id"), params.value("name")
        temp = request.app.get("used").get("detail")
        temp = "web".format(temp) if temp.startswith("/") else "web/{0}".format(temp)
        print("detail渲染模板：", temp)
        foreign, tableName, relatedName = getForeign(True), getTableName(True), getTableName(False)
        template, isDetail = getTemplate(path), "deep" in selectTable(False).get("detail", {})
        return render(temp, type="", path=path, related=id, detail="{0}-详情：".format(name), foreign=foreign,
                      tableName=tableName, relatedName=relatedName, template=template, isDetail=isDetail)

    @bp.route("/detail/list", methods=["POST", "GET"])
    def detailList():
        # params = Bigdata(db, request, pops="id")
        params = factoryDB(True, pops="id")
        foreign = getForeign(True)
        return json.dumps(params.findBy(foreign, orderBy="order by number ASC,id DESC"))

    @bp.route("/detail/add", methods=["POST", "GET"])
    def detailAdd():
        # params = Bigdata(db, request, pops="id", byNames="exhibit")
        foreign = getForeign(True)
        params = factoryDB(True, pops="id", byNames=foreign)
        return json.dumps(params.insert(orderBy="order by number ASC,id DESC"))

    @bp.route("/detail/update", methods=["POST", "GET"])
    def detailUpdate():
        # params = Bigdata(db, request, pops="id", byNames="exhibit")
        foreign = getForeign(True)
        params = factoryDB(True, pops="id", byNames=foreign)
        return json.dumps(params.updateById(orderBy="order by number ASC,id DESC"))

    @bp.route("/detail/del", methods=["POST", "GET"])
    def detailDelete():
        # params = Bigdata(db, request, pops="id", byNames="exhibit")
        foreign = getForeign(True)
        params = factoryDB(True, pops="id", byNames=foreign)
        return json.dumps(params.deleteById(orderBy="order by number ASC,id DESC"))

    # 第三层内页
    @bp.route("/deep", methods=["POST", "GET"])
    def index_deep():
        path = request.path
        path = path if path.endswith("/") else "{0}/".format(path)
        params = Requester(request)
        id, name = params.value("id"), params.value("name")
        temp = request.app.get("used").get("deep")
        temp = "web".format(temp) if temp.startswith("/") else "web/{0}".format(temp)
        print("detail渲染模板：", temp)
        foreign, tableName, relatedName = getForeign(True), getTableName(True), getDetailName()
        template = getTemplate(path)
        return render(temp, type="", path=path, related=id, detail="{0}-详情：".format(name), foreign=foreign,
                      tableName=tableName, relatedName=relatedName, template=template, isDetail=False)

    @bp.route("/deep/list", methods=["POST", "GET"])
    def deepList():
        # params = Bigdata(db, request, pops="id")
        params = factoryDB(True, pops="id")
        foreign = getForeign(True)
        return json.dumps(params.findBy(foreign, orderBy="order by number ASC,id DESC"))

    @bp.route("/deep/add", methods=["POST", "GET"])
    def deepAdd():
        # params = Bigdata(db, request, pops="id", byNames="exhibit")
        foreign = getForeign(True)
        params = factoryDB(True, pops="id", byNames=foreign)
        return json.dumps(params.insert(orderBy="order by number ASC,id DESC"))

    @bp.route("/deep/update", methods=["POST", "GET"])
    def deepUpdate():
        # params = Bigdata(db, request, pops="id", byNames="exhibit")
        foreign = getForeign(True)
        params = factoryDB(True, pops="id", byNames=foreign)
        return json.dumps(params.updateById(orderBy="order by number ASC,id DESC"))

    @bp.route("/deep/del", methods=["POST", "GET"])
    def deepDelete():
        # params = Bigdata(db, request, pops="id", byNames="exhibit")
        foreign = getForeign(True)
        params = factoryDB(True, pops="id", byNames=foreign)
        return json.dumps(params.deleteById(orderBy="order by number ASC,id DESC"))

    @bp.route("/assist/<path:operate>/<path:tableName>", methods=["POST", "GET"])
    def operate(operate, tableName):
        res = {"success": False, "data": [], "msg": "查询失败！"}
        if operate == "query":
            type_ = request.args.get("type")
            table = getTable(tableName, pops="id")
            res = json.dumps(table.findBy(whereBy="where type='{0}'".format(type_)))
        return res

    # @bp.route("detail/assist/<path:operate>/<path:tableName>", methods=["POST", "GET"])
    # def operate_detail(operate, tableName):
    #     res = {"success": False, "data": [], "msg": "查询失败！"}
    #     if operate == "query":
    #         type_ = request.args.get("type")
    #         table = getTable(tableName, pops="id")
    #         res = json.dumps(table.findBy(whereBy="where type='{0}'".format(type_)))
    #     return res

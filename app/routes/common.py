import json
from app.models.Common import factoryDB
from flask import render_template as render, redirect, request
from libs.Viewer import Requester

def getForeign(request, detail=False):
    table = request.app.get("used", {}).get("table")
    return table.get("detail", {}).get("foreign", []) if detail else table.get("foreign", [])

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
        return render(temp, type="", path=path)

    @bp.route("/list", methods=["POST", "GET"])
    def screenList():
        # params = Bigdata(db, request, pops="id")
        params = factoryDB(False, pops="id")
        foreign = getForeign(request)
        return json.dumps(params.findBy(foreign, orderBy="order by number ASC,id DESC"))

    @bp.route("/add", methods=["POST", "GET"])
    def screenAdd():
        # params = Bigdata(db, request, pops="id", byNames="exhibit")
        foreign = getForeign(request)
        params = factoryDB(False, pops="id", byNames=foreign)
        return json.dumps(params.insert(orderBy="order by number ASC,id DESC"))

    @bp.route("/update", methods=["POST", "GET"])
    def screenUpdate():
        # params = Bigdata(db, request, pops="id", byNames="exhibit")
        foreign = getForeign(request)
        params = factoryDB(False, pops="id", byNames=foreign)
        return json.dumps(params.updateById(orderBy="order by number ASC,id DESC"))

    @bp.route("/del", methods=["POST", "GET"])
    def screenDelete():
        # params = Bigdata(db, request, pops="id", byNames="exhibit")
        foreign = getForeign(request)
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
        return render(temp, type="", path=path, related=id, detail="{0}-详情：".format(name))

    @bp.route("/detail/list", methods=["POST", "GET"])
    def detailList():
        # params = Bigdata(db, request, pops="id")
        params = factoryDB(True, pops="id")
        foreign = getForeign(request, True)
        return json.dumps(params.findBy(foreign, orderBy="order by number ASC,id DESC"))

    @bp.route("/detail/add", methods=["POST", "GET"])
    def detailAdd():
        # params = Bigdata(db, request, pops="id", byNames="exhibit")
        foreign = getForeign(request, True)
        params = factoryDB(True, pops="id", byNames=foreign)
        return json.dumps(params.insert(orderBy="order by number ASC,id DESC"))

    @bp.route("/detail/update", methods=["POST", "GET"])
    def detailUpdate():
        # params = Bigdata(db, request, pops="id", byNames="exhibit")
        foreign = getForeign(request, True)
        params = factoryDB(True, pops="id", byNames=foreign)
        return json.dumps(params.updateById(orderBy="order by number ASC,id DESC"))

    @bp.route("/detail/del", methods=["POST", "GET"])
    def detailDelete():
        # params = Bigdata(db, request, pops="id", byNames="exhibit")
        foreign = getForeign(request, True)
        params = factoryDB(True, pops="id", byNames=foreign)
        return json.dumps(params.deleteById(orderBy="order by number ASC,id DESC"))

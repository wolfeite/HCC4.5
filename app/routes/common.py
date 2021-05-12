import json
from app.models.Common import factoryDB, getTable, getSheet, getTier, getTemplate
from flask import render_template as render, request
from libs.analyser.Viewer import Requester

def add_route(bp, **f):
    db = f["db"]

    @bp.route("/", methods=["POST", "GET"])
    def index():
        path, tier = request.path, getTier()
        path = path if path.endswith("/") else "{0}/".format(path)
        temp, sheet, children, params = tier.get("temp"), tier.get("sheet"), tier.get("children"), Requester(request)
        temp = "web".format(temp) if temp.startswith("/") else "web/{0}".format(temp)
        # return render_template("web/common/index.html", type="", path=path)
        print("index渲染模板：", temp)
        id, name, child = params.value("id"), params.value("name"), params.value("child")
        foreign, tableName, template = sheet.get("foreign"), sheet.get("name"), getTemplate(path)
        isDetail, relatedName, detail = tier.get("isDetail"), tier.get("related"), "{0}-详情：".format(
            name) if name else None
        return render(temp, type="", path=path, foreign=foreign, tableName=tableName, template=template,
                      isDetail=isDetail, related=id, relatedName=relatedName, detail=detail, children=children)

    @bp.route("/list", methods=["POST", "GET"])
    def screenList():
        foreign = getSheet().get("foreign", [])
        params = factoryDB(pops="id")
        return json.dumps(params.findBy(foreign, orderBy="order by number ASC,id DESC"))

    @bp.route("/add", methods=["POST", "GET"])
    def screenAdd():
        foreign = getSheet().get("foreign", [])
        params = factoryDB(pops="id", byNames=foreign)
        return json.dumps(params.insert(orderBy="order by number ASC,id DESC"))

    @bp.route("/update", methods=["POST", "GET"])
    def screenUpdate():
        foreign = getSheet().get("foreign", [])
        params = factoryDB(pops="id", byNames=foreign)
        return json.dumps(params.updateById(orderBy="order by number ASC,id DESC"))

    @bp.route("/del", methods=["POST", "GET"])
    def screenDelete():
        foreign = getSheet().get("foreign", [])
        params = factoryDB(pops="id", byNames=foreign)
        return json.dumps(params.deleteById(orderBy="order by number ASC,id DESC"))

    @bp.route("/assist/<path:operate>/<path:tableName>", methods=["POST", "GET"])
    def operate(operate, tableName):
        res = {"success": False, "data": [], "msg": "查询失败！"}
        if operate == "query":
            type_ = request.args.get("type")
            table = getTable(tableName, pops="id")
            res = json.dumps(table.findBy(whereBy="where type='{0}'".format(type_)))
        return res

    @bp.route("/sort", methods=["POST", "GET"])
    def screenSort():
        # params =Requester(request)
        foreign = getSheet().get("foreign", [])
        params, orderBy = factoryDB(pops="id"), "order by number ASC,id DESC"
        sort, data = params.requester.value("sort"), params.model.find("*", clause=orderBy).get("data", [])
        data = data[::-1] if sort == "reverse" else data
        print(">>>>>>>>>>>sort>>>>>>>>>>", data)
        for i, v in enumerate(data): params.model.update({"number": i + 1}, clause="where id={0}".format(v["id"]))
        # params.updateById(orderBy="order by number ASC,id DESC")
        return json.dumps(params.findBy(foreign, orderBy=orderBy))

    # @bp.route("detail/assist/<path:operate>/<path:tableName>", methods=["POST", "GET"])
    # def operate_detail(operate, tableName):
    #     res = {"success": False, "data": [], "msg": "查询失败！"}
    #     if operate == "query":
    #         type_ = request.args.get("type")
    #         table = getTable(tableName, pops="id")
    #         res = json.dumps(table.findBy(whereBy="where type='{0}'".format(type_)))
    #     return res

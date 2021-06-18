import json
from libs.io import File, Json
from libs.util import Path
from app.models.Common import factoryDB
import os, shutil, requests
from flask import request
from libs.analyser.Viewer import Requester
from app.models.pattern import ViewModel

def confirmSheet(_key, tables):
    table = tables.get(_key)
    if not table:
        table = tables.get("_")
        table = list(tables.values())[0] if not table else table
    return table

def getDeepData(db, url, parent_obj, parentData, parentName, orderBy):
    deep_obj = parent_obj.get("deep", [])
    deep_obj = deep_obj if isinstance(deep_obj, (list, tuple)) else [deep_obj]
    if deep_obj:
        for dv in deep_obj:
            nm_deep = dv.get("name", "deep")
            col_nm_deep = dv.get("column_name", nm_deep)
            deep, url_deep = db.models[nm_deep], "{0}deep/".format(url)
            for j, d in enumerate(parentData):
                clause_d = "where route='{0}' and {1}={2} {3}".format(url_deep, parentName, d.get("id"), orderBy)
                d[col_nm_deep] = deep.find("*", clause=clause_d).get("data", [])
                getDeepData(db, url, dv, d[col_nm_deep], nm_deep, orderBy)

def getData(db, table, url, orderBy):
    table_name = table.get("name", "screen")
    url = url if url.endswith("/") else "{0}/".format(url)
    data_res = db.models[table_name].find("*", clause="where route='{0}' {1}".format(url, orderBy)).get(
        "data", [])
    detail_obj = table.get("detail")
    if detail_obj:
        detail_obj = detail_obj if isinstance(detail_obj, (list, tuple)) else [detail_obj]
        for v in detail_obj:
            nm_detail = v.get("name", "detail")
            col_nm_detail = v.get("column_name", nm_detail)
            detail, url_detail = db.models[nm_detail], "{0}detail/".format(url)
            # detail_foreign = detail_obj.get("foreign", [])

            deep_obj, col_nm_deep, nm_deep, deep, url_deep = v.get("deep", []), None, None, None, None
            if deep_obj:
                deep_obj = deep_obj if isinstance(deep_obj, (list, tuple)) else [deep_obj]

            for i, r in enumerate(data_res):
                clause = "where route='{0}' and {1}={2} {3}".format(url_detail, table_name, r.get("id"), orderBy)
                r[col_nm_detail] = detail.find("*", clause=clause).get("data", [])

                getDeepData(db, url, v, r[col_nm_detail], nm_detail, orderBy)
                # for dv in deep_obj:
                #     nm_deep = dv.get("name", "deep")
                #     col_nm_deep = dv.get("column_name", nm_deep)
                #     deep, url_deep = db.models[nm_deep], "{0}deep/".format(url)
                #     for j, d in enumerate(r[col_nm_detail]):
                #         clause_d = "where route='{0}' and {1}={2} {3}".format(url_deep, nm_detail, d.get("id"), orderBy)
                #         d[col_nm_deep] = deep.find("*", clause=clause_d).get("data", [])
    return data_res

def add_route(bp, **f):
    db = f["db"]
    @bp.route("/toJson", methods=["POST", "GET"])
    def toJson():
        db = request.app.get("db")
        to_json = Json(("data"))
        routes, tables = request.app.get("routes", {}), request.app.get("tables", {})
        json_data, orderBy, res = {}, "order by number ASC,id DESC", {"success": True}
        for route_key in routes:
            route = routes[route_key]
            url = route.get("url")
            if not url in ["#"]:
                table = confirmSheet(route_key, tables)
                name, item = route.get("name", route_key), route.get("item")
                url = url if url else "/{0}".format(route_key)
                if item:
                    json_data[name] = {}
                    for i in item:
                        name_, url_ = i.get("name", route_key), i.get("url", "/{0}".format(route_key))
                        json_data[name][name_] = getData(db, table, url_, orderBy)
                else:
                    json_data[name] = getData(db, table, url, orderBy)
        to_json.write("data.json", json_data)
        res["data"] = json_data
        return json.dumps(res)

    @bp.route("/moveTo", methods=["POST", "GET"])
    @bp.route("/moveTo/<path:table>/<path:url>", methods=["POST", "GET"])
    def moveTo(table="", url=""):
        res, orderBy, resData = {"success": True}, "order by number ASC,id DESC", {}
        if not table or not url:
            res["success"] = False
            res["msg"] = "缺少参数！"
            return json.dumps(res)

        db = request.app.get("db")
        resData = db.models[table].find("*", clause="where route='{0}' {1}".format("/audio/", orderBy)).get(
            "data", [])
        dirPath, disPath = Path(("data", "statics", "audio")).dir, Path(("data", "mp3"), mk=True).dir
        for i, val in enumerate(resData):
            tag, path = "{0}.wav".format(val["id"]), val["path"]
            dirFile, disFile = Path.join(dirPath, path), Path.join(disPath, tag)
            if path and os.path.isfile(dirFile):
                shutil.copyfile(dirFile, disFile)
        res["msg"] = "音频转移完成！"
        return json.dumps(res)

    @bp.route("/query/<path:table>", methods=["POST", "GET"])
    @bp.route("/query/<path:table>/<path:sep>", methods=["POST", "GET"])
    def query(table, sep="_"):
        # 查询
        db, args, orderBy = request.app.get("db"), request.args, "order by number ASC,id DESC"
        names, res = table.split(sep), {}
        clauseWhere = [("{0}='{1}'" if isinstance(v, str) else "{0}={1}").format(i, v) for i, v in args.items()]
        clause = " and ".join(clauseWhere)
        orderBy = "where {0} {1}".format(clause, orderBy) if clause else orderBy
        # print("where {0} {1}".format(clause, orderBy))
        for name in names:
            res[name] = db.models[name].find("*", clause=orderBy).get("data", []) if name in db.models else []
        return json.dumps(res)

    @bp.route("/up/<path:table>", methods=["POST", "GET"])
    def up(table):
        # 表单上传并入数据表
        db, orderBy, rt = request.app.get("db"), "order by number ASC,id DESC", {"route": "/{0}/".format(table)}
        res = ViewModel(db, table, request, pops="id", extra=rt).insert(orderBy=orderBy) if table in db.models else {}
        return json.dumps(res)

    @bp.route("/orderJson/<path:table>", methods=["POST", "GET"])
    def orderJson(table):
        db, args, orderBy = request.app.get("db"), request.args, "order by number ASC,id DESC"
        # data = requests.get("http://{0}/api/query/{1}".format(request.host, table)).json()
        data_cmd = db.models[table].find("*", clause=orderBy).get("data", [])
        res, base = {"success": False}, Json(("data", "order.json"))
        resData = {"commands": {}, "human": {}, "request": {}}
        baseData = base.result

        mapping = {
            "server": {"ws": "wss", "tcp": "ts", "udp": "us"},
            "client": {"ws": "wsc", "tcp": "tc", "udp": "uc"},
            "value": ["ip", "port", "tag", "manner", "opts", "addition"]
        }
        items, data_ser = {}, db.models["services"].find("*", clause=orderBy).get("data", [])
        for index, v in enumerate(data_ser):
            r = v.get("route")
            key_cal = "localhost" if "server" in r else "host"
            items[key_cal] = items.get(key_cal, {})
            type, modal = v["type"], v["modal"]
            key, option = mapping[type][modal], {}

            print("key", key_cal, key)
            items[key_cal][key] = items[key_cal].get(key, {})
            val = items[key_cal][key]
            print("val", val)
            items[key_cal][key] = [val] if val and isinstance(val, dict) else val

            for k in mapping["value"]:
                try:
                    _val_ = json.loads(v[k])
                except Exception as e:
                    _val_ = v[k]

                if k == "opts" or k == "addition":
                    if isinstance(_val_, dict): option.update(_val_)
                else:
                    option[k] = _val_
            if isinstance(items[key_cal][key], dict):
                items[key_cal][key] = option
            else:
                items[key_cal][key].append(option)
        baseData.update(items)

        for i, val in enumerate(data_cmd):
            r = val.get("route")
            rData = resData["commands"] if "third" in r else resData["human"]
            try:
                rData[val["key"]] = json.loads(val["value"])
            except Exception as e:
                rData[val["key"]] = val["value"]
        baseData.update(resData)

        base.write("order.json", baseData)

        data_app = db.models["app"].find("*", clause=orderBy).get("data", [])
        base_app, btns = Json(("data", "app.json")), {"btns": []}
        for j, v in enumerate(data_app):
            btn = {}
            btn.update(v)
            btn["codes"] = json.loads(v["codes"])
            btns["btns"].append(btn)

        base_app_data = base_app.result
        base_app_data.update(btns)
        base_app.write("app.json", base_app_data)

        res = {"success": True, "msg": "保存成功"}
        return json.dumps(res)

    @bp.route("/test", methods=["POST", "GET"])
    def test():
        # 链接测试接口
        res = request.values if request.values else getattr(request, "json", {})
        print("收到参数为", res)
        res = {"success": True, "data": res}
        return json.dumps(res)

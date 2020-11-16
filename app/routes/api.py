import json
from libs.io import File, Json
from app.models.Common import factoryDB
import os
from flask import request

def getData(db, table, url, orderBy):
    table_name = table.get("name", "screen")
    url = url if url.endswith("/") else "{0}/".format(url)
    data_res = db.models[table_name].find("*", clause="where route='{0}' {1}".format(url, orderBy)).get(
        "data", [])
    detail_obj = table.get("detail")
    if detail_obj:
        column_name = detail_obj.get("column_name", "details")
        detail_name = detail_obj.get("name", "detail")
        detail, url = db.models[detail_name], "{0}detail/".format(url)
        detail_foreign = detail_obj.get("foreign", [])
        for i, r in enumerate(data_res):
            foreign_clause = []
            for j, f in enumerate(detail_foreign):
                val = r.get("id")
                strCal = "{0}='{1}'" if isinstance(val, str) else "{0}={1}"
                (not f == "route") and foreign_clause.append(strCal.format(f, val))
            clause = "where route='{0}' and {1} {2}".format(url, " and ".join(foreign_clause), orderBy)
            r[column_name] = detail.find("*", clause=clause).get("data", [])
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
            if not route_key == "toJson":
                route = routes[route_key]
                table = tables.get(route_key, {}) if len(tables) > 1 else list(tables.values())[0]
                item = route.get("item")
                name, url = route.get("name", route_key), route.get("url", "/{0}".format(route_key))
                if item :
                    json_data[name]={}
                    for i in item:
                        name_, url_ = i.get("name", route_key), i.get("url", "/{0}".format(route_key))
                        json_data[name][name_] = getData(db, table, url_, orderBy)
                else:
                    json_data[name] = getData(db, table, url, orderBy)
        to_json.write("data.json", json_data)
        res["data"] = json_data
        return json.dumps(res)

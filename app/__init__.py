from .routes import filter, api, sign, common
from app.config import secure
from app.config import setting
from app.initDataBase import init_db

def createMode(db, t, defCol, others_foreign=["route"]):
    tagCol, name, col, foreign = {}, t.get("name"), t.get("column"), t.get("foreign", [])
    foreign = [foreign] if not isinstance(foreign, list) else foreign
    t["foreign"] = list(set(foreign + others_foreign))  # 列表合并去重
    if col and isinstance(col, dict):
        tagCol.update(defCol)
        tagCol.update(col)
        for f in t["foreign"]:
            if not f == "route":
                tagCol[f] = "int not null references {0}(id) on delete cascade".format(f)
        db.model(name, tagCol)

def config_jinja(app):
    app.flask.add_template_global(app.config["ASIDE"], 'aside')
    app.flask.add_template_global(app.config["ENV"], 'env')
    app.flask.add_template_global(app.config["CHANGE"], 'change')
    app.flask.add_template_global(app.config["TITLE"], 'title')

    @app.flask.template_filter('parserPath')
    def parserPath(arr):
        res = []
        for val in arr:
            not val == "" and res.append(val)
        return res

def init_app_db(db, app):
    tables = app.config.get("TABLES", {})
    defCol = {
        "id": "integer not null primary key autoincrement unique",
        "number": "integer default 1",
        "route": "text not null",
    }
    index_col, detail_col = {}, {}
    for t_key in tables:
        t = tables[t_key]
        t_nm, detail = t.get("name", "screen"), t.get("detail")
        t["name"] = t_nm
        createMode(db, t, defCol, ["route"])
        if detail and isinstance(detail, dict):
            detail_nm, deep = detail.get("name", "detail"), detail.get("deep")
            detail["name"] = detail_nm
            createMode(db, detail, defCol, ["route", t_nm])
            if deep and isinstance(deep, dict):
                deep_nm = deep.get("name", "deep")
                deep["name"] = deep_nm
                createMode(db, deep, defCol, ["route", detail_nm])
        # name, col, foreign = t.get("name", "screen"), t.get("column", None), t.get("foreign", [])
        # foreign = [foreign] if not isinstance(foreign, list) else foreign
        # t["foreign"] = foreign
        # if col and isinstance(col, dict):
        #     index_col.update(defCol)
        #     index_col.update(col)
        #     for f in foreign:
        #         if not f == "route":
        #             index_col[f] = "int not null references {0}(id) on delete cascade".format(f)
        #     db.model(name, index_col)
        #     (not "route" in foreign) and t["foreign"].append("route")
        #     det = t.get("detail", None)
        #     if det and isinstance(det, dict):
        #         name_, col_, foreign_ = det.get("name", "detail"), det.get("column", None), det.get("foreign", [])
        #         foreign_ = [foreign_] if not isinstance(foreign_, list) else foreign_
        #         det["foreign"] = foreign_
        #         if col_ and isinstance(col_, dict):
        #             detail_col.update(defCol)
        #             detail_col.update(col_)
        #             # "related": "int not null references screen(id) on delete cascade",
        #             detail_col[name] = "int not null references {0}(id) on delete cascade".format(name)
        #             for f_ in foreign_:
        #                 if not f_ == name and not f_ == "route":
        #                     detail_col[f_] = "int not null references {0}(id) on delete cascade".format(f_)
        #             db.model(name_, detail_col)
        #             (not name in foreign_) and det["foreign"].append(name)
        #             (not "route" in foreign_) and det["foreign"].append("route")
    print(">>>>处理后的tables", tables)
    # screen = db.model("screen", {
    #     "id": "integer not null primary key autoincrement unique",  # 主键
    #     "number": "integer default 1",  # 序号
    #     "route": "text not null",  # 路由路径
    #     "year": "integer",  # 年份
    #     "date": "text",  # 时间
    #     "info": "text not null",  # 信息
    #     "ImagePath": "text"  # 图片
    # })
    # detail = db.model("detail", {
    #     "id": "integer not null primary key autoincrement unique",  # 主键
    #     "number": "integer default 1",  # 序号
    #     "related": "int not null references screen(id) on delete cascade",  # screen外键
    #     "name": "text",  # 图片名称
    #     "path": "text"  # 路径
    # })

def config_app(app):
    app.config = (secure, setting)
    init_db(app, init_app_db)
    config_jinja(app)
    print(">>>>app.root_path:", app.flask.root_path)
    app.register_filter(filter.exec)

    app.register_router("api", __name__, api.add_route, url_prefix="/api")
    app.register_router("sign", __name__, sign.add_route, url_prefix="/sign")

    routes = app.config["ROUTES"]
    print(">>>>", routes)
    for route_key in routes:
        route = routes[route_key]
        if not route_key in ["toJson", "toUpdate"]:
            url_prefix, name, item = route.get("url"), route.get("name"), route.get("item", [])
            print("注册路由》》》", name, url_prefix)
            app.register_router(name, __name__, common.add_route, url_prefix=url_prefix)
            if len(item) > 0:
                for r in item:
                    name, url_prefix, = r.get("name"), r.get("url")
                    print("注册item中的路由》》》", name, url_prefix)
                    app.register_router(name, __name__, common.add_route, url_prefix=url_prefix)

    # app.register_router("perfect", __name__, common.add_route, url_prefix="/perfect")
    # app.register_router("business_image", __name__, common.add_route, url_prefix="/business/image")
    # app.register_router("business_data", __name__, common.add_route, url_prefix="/business/data")
    # app.register_router("activity_image", __name__, common.add_route, url_prefix="/activity/image")
    # app.register_router("activity_video", __name__, common.add_route, url_prefix="/activity/video")

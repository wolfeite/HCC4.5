from .routes import filter, api, sign, common
from app.config import secure
from app.config import setting
from app.initDataBase import init_db

def register_router_common(app, name, url, is_detail={}, is_deep={}):
    register_router(app, name, common, url)
    check_url = url if url.endswith("/") else "{0}/".format(url)
    is_detail and register_router(app, "{0}_detail".format(name), common, "{0}detail".format(check_url))
    is_deep and register_router(app, "{0}_deep".format(name), common, "{0}deep".format(check_url))

def register_router(app, name, router, url_prefix):
    app.register_router(name, __name__, router.add_route, url_prefix=url_prefix)

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

    print(">>>>处理后的tables", tables)

def config_app(app):
    app.config = (secure, setting)
    init_db(app, init_app_db)
    config_jinja(app)
    print(">>>>app.root_path:", app.flask.root_path)
    app.register_filter(filter.exec)

    app.register_router("api", __name__, api.add_route, url_prefix="/api")
    app.register_router("sign", __name__, sign.add_route, url_prefix="/sign")

    # 添加路由
    routes = app.config["ROUTES"]
    for route_key in routes:
        route = routes[route_key]
        if not route_key in ["toJson", "toUpdate"]:
            url_prefix, name, item = route.get("url"), route.get("name"), route.get("item", [])
            has_detail, has_deep = route.get("has_detail", {}), route.get("has_deep", {})
            print("注册路由》》》", name, url_prefix)
            if len(item) > 0:
                for r in item:
                    name, url_prefix, = r.get("name"), r.get("url")
                    print("注册item中的路由》》》", name, url_prefix)
                    register_router_common(app, name, url_prefix, has_detail, has_deep)
                    # app.register_router(name, __name__, common.add_route, url_prefix=url_prefix)
            else:
                register_router_common(app, name, url_prefix, has_detail, has_deep)
                # app.register_router(name, __name__, common.add_route, url_prefix=url_prefix)

    # app.register_router("perfect", __name__, common.add_route, url_prefix="/perfect")
    # app.register_router("business_image", __name__, common.add_route, url_prefix="/business/image")
    # app.register_router("business_data", __name__, common.add_route, url_prefix="/business/data")
    # app.register_router("activity_image", __name__, common.add_route, url_prefix="/activity/image")
    # app.register_router("activity_video", __name__, common.add_route, url_prefix="/activity/video")

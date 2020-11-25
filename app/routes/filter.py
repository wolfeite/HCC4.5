from flask import Flask, render_template, request, abort, g, redirect, url_for, session
import copy

def filterPath(request, *args):
    ignore = request.app["ignore"]
    ignore = ignore + list(args)
    res = False
    for key in ignore:
        if request.path.startswith(key):
            res = True
            break
    return res

def confirmSheet(_key, tables):
    table = tables.get(_key)
    if not table:
        table = tables.get("_")
        table = list(tables.values())[0] if not table else table
    return table

def exec(flaskApp, **f):
    print("app>>>>>>>httpServer", flaskApp)
    # g.root_path = flaskApp.root_path
    @flaskApp.before_request
    def auther():
        # path = request.path
        request.app = {}
        enter, login, super = flaskApp.config["ENTER"], flaskApp.config["LOGIN"], flaskApp.config.get("SUPER")
        isFree = enter == login.FREE.value
        request.app["isFree"], request.app["ignore"] = isFree, flaskApp.config["IGNORE"]
        request.app["routes"] = flaskApp.config["ROUTES"]  # api中使用
        request.app["db"], request.app["tables"] = f["db"], flaskApp.config["TABLES"]
        # request.app["tableUsed"] = None
        request.app["used"] = {"index": "common/index.html", "detail": "common/detail.html", "table": None}
        request.app["root"] = flaskApp.root_path
        request.app["template"] = flaskApp.config["TEMPLATE"]

        if filterPath(request):
            return None
        # if request.path == "/favicon.ico":
        #     # abort(200)

        print("登入判断：", enter, login.FREE.value, enter == login.FREE.value)
        if isFree:
            session.clear()
            session["user"] = {"id": super.ID.val, "number": super.NUMBER.val, "name": super.NAME.val,
                               "nickname": super.NICKNAME.val, "rank": super.RANK.value, "theme": super.THEME.val}

        user = session.get("user")
        if not user:
            print(">>>进入登入页")
            return redirect(url_for("sign.login"))

        return None

    @flaskApp.before_request
    def parserAside():
        request.app["pathsName"] = []

        rootAside = []

        # 获取平台模式
        version = f["db"].models["version"]
        res = version.find("*", clause="where number=3.7")

        mode = flaskApp.config["MODE"]
        mode_defVal = mode.DEFAULT.value
        pat = int(mode_defVal if len(res["data"]) == 0 else res["data"][0].get("pattern", mode_defVal))
        print("当前平台模式为：", pat)
        flaskApp.add_template_global(pat, 'pattern')
        request.app["pattern"] = pat
        request.app["mode"] = mode

        if filterPath(request):
            return None
        # rootAside = copy.deepcopy(flaskApp.config["ASIDE"])
        aside = copy.deepcopy(flaskApp.config["ASIDE"])

        rights = flaskApp.config["RIGHTS"]
        user = session.get("user")
        rank = user["rank"] if user else rights.DEFAULT.value
        hasPath = []
        def filterAside(items):
            r, p = items.get("rights", rights.DEFAULT.value), items.get("pat", pat)
            if rank >= r and pat == p:
                children = items.get("item", [])
                url_items = items.get("url")
                url_items and hasPath.append(url_items)
                for item in children[:]:
                    not filterAside(item) and children.remove(item)
                return True
            else:
                return False
        rootAside = list(filter(filterAside, aside))
        request.app["aside"] = rootAside

        request.app["hasPath"] = hasPath

        for val in rootAside:
            if request.path.startswith(val["url"]):
                tables = request.app["tables"]
                _key = val.get("key")
                request.app["used"]["table"] = confirmSheet(_key, tables)
                # request.app["tableUsed"] = list(tables.values())[0] if len(tables) == 1 else tables.get(_key, None)
                request.app["used"]["index"] = val.get("index", "common/index.html")
                request.app["used"]["detail"] = val.get("detail", "common/detail.html")
                request.app["used"]["deep"] = val.get("deep", "common/deep.html")
                print(request.path, ">>>>>>采用的used为：", _key, request.app["used"])
                request.app["pathsName"].append(val["title"])
                if val.get("item") and len(val["item"]) > 0:
                    for cval in val["item"]:
                        request.path.startswith(cval["url"]) and request.app["pathsName"].append(cval["title"])
                break

    @flaskApp.before_request
    def pathsFilter():
        if filterPath(request):
            return None
        path, res, paths = request.path, False, request.app["hasPath"]
        for val in paths:
            if val in path:
                res = True
                break
        print(path, "{0}配置的{1}路由中".format("在" if res else "不在", paths))
        # if path == "/" or path == "/index" or not res:
        if not res:
            # 首页/默认页
            return redirect(flaskApp.config["INDEX"])

    @flaskApp.after_request
    def excp(response):
        if not filterPath(request):
            print("《《《《app请求结果处理器", request.path, response)
        return response
    # register_route(app)

    # # 在请求之后,出现异常时执行
    # @app.teardown_request
    # def teardown_request(e):
    #     # 在请求之后,必须接受异常作为参数
    #     print("teardown_request" + "异常:" + str(e), request.path)

    if flaskApp.config["ENV"] == "production":
        @flaskApp.errorhandler(404)
        def error_404(error_info):
            # werkzeug.exceptions.InternalServerError
            # werkzeug.exceptions.NotFound
            if filterPath(request):
                headers = {"content-type": "text/plain"}
                return "<html>过滤资源没有找到！</html>", 404, headers
            else:
                path = request.path
                print("not found 404>>>>>>>>>>>>>>>>>", path, type(error_info))
                return render_template("templates/error.html", error=error_info)

        # @flaskApp.errorhandler(Exception)
        # def error_other(error):
        #     """这个handler可以catch住所有的abort(500)和raise exeception."""
        #     response = dict(status=0, message="500 Error")
        #     if not filterPath(request):
        #         print("other_error:", type(error), ">>>>>", error, request.path)
        #     return render_template("templates/error.html", error=error)

    # 注意debug模式下只能在主线程中
    # app.run(host="0.0.0.0", debug=app.config["DEBUG"], port=app.config["PORT"])

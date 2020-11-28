from flask import Flask, render_template, request, abort, g, redirect, url_for, session
import copy

def checkUrlTier(path, prefix_url, used):
    # 3层 index,detail,deep
    url, tier = prefix_url if prefix_url.endswith("/") else "{0}/".format(prefix_url), used.get("tier")
    if path.startswith(prefix_url):
        used["tier"], detail, deep = "index", "{0}detail".format(url), "{0}deep".format(url)
        if path.startswith(detail):
            used["tier"] = "detail"
        elif path.startswith(deep):
            used["tier"] = "deep"

def filterPath(request, *args):
    ignore = request.app["ignore"]
    ignore = ignore + list(args)
    res = False
    for key in ignore:
        if request.path.startswith(key):
            res = True
            break
    return res

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
        request.app["db"], request.app["tables"] = f["db"], flaskApp.config["TABLES"]  # api中使用
        request.app["used"] = {}
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
                # tables = request.app["tables"]
                _key, has_detail, has_deep = val.get("key"), val["has_detail"], val["has_deep"]
                index_detail, detail_detail = True if has_detail else False, True if has_deep else False
                temp_index, temp_detail, temp_deep = "common/index.html", "common/detail.html", "common/deep.html"
                request.app["used"] = {
                    "table": val["table"], "prefix": val["url"], "tier": None,
                    "index": {"temp": val.get("index", temp_index), "sheet": val["table"], "isDetail": index_detail},
                    "detail": {"temp": val.get("detail", temp_detail), "sheet": has_detail, "isDetail": detail_detail,
                               "related": val["table"].get("name")},
                    "deep": {"temp": val.get("deep", temp_deep), "sheet": has_deep, "related": has_detail.get("name")}
                }

                checkUrlTier(request.path, val["url"], request.app["used"])
                # request.app["used"]["table"] = confirmSheet(_key, tables)
                # request.app["used"]["index"] = val.get("index", "common/index.html")
                # request.app["used"]["detail"] = val.get("detail", "common/detail.html")
                # request.app["used"]["deep"] = val.get("deep", "common/deep.html")
                # request.app["used"]["prefix"] = val["url"]
                request.app["pathsName"].append(val["title"])
                if val.get("item") and len(val["item"]) > 0:
                    for cval in val["item"]:
                        checkUrlTier(request.path, cval["url"], request.app["used"])
                        request.path.startswith(cval["url"]) and request.app["pathsName"].append(cval["title"])
                print(request.path, ">>>>>>采用的used为：", _key, request.app["used"])
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
            index = flaskApp.config["INDEX"]
            return redirect(index if index in paths else paths[0])

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

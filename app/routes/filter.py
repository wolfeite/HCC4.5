from flask import Flask, render_template, request, abort, g, redirect, url_for, session
import copy, json

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

def is_xhr(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"

def getTemp(val, defval, child=""):
    return val.get(child, defval) if isinstance(val, dict) else val if isinstance(val, str) else defval

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
                _key = val.get("key")
                request.app["used"] = {"prefix": val["url"], "tier": None}
                request.app["pathsName"].append(val["title"])

                if val.get("item") and len(val["item"]) > 0:
                    for cval in val["item"]:
                        if request.path.startswith(cval["url"]):
                            # checkUrlTier(request.path, cval["url"], request.app["used"])
                            # tier = request.app["used"].get("tier")
                            # request.app["used"][tier] = used.get(tier)
                            request.app["pathsName"].append(cval["title"])
                            val = cval
                            break

                checkUrlTier(request.path, val["url"], request.app["used"])

                # tables = request.app["tables"]
                # print("使用的路由表为>>>>>", val)
                has_detail, has_deep = val["has_detail"], val["has_deep"]
                is_detail, is_deep = True if has_detail else False, True if has_deep else False
                temp_index, temp_detail, temp_deep = "common/index.html", "common/detail.html", "common/deep.html"

                child = request.args.get("child")
                index_tab, detail_tab, deep_tab = val["table"], has_detail.get(child, {}), has_deep.get(child, {})
                index_nm = index_tab.get("name")

                index_children = list(has_detail.keys()) if has_detail else []
                detail_children = [k for k, v in has_deep.items() if child == v.get("parent")]

                index, detail, deep = val.get("index"), val.get("detail"), val.get("deep")
                temp_index = index if isinstance(index, str) else temp_index
                temp_detail = getTemp(detail, temp_detail, child)
                temp_deep = getTemp(deep, temp_deep, child)
                # print("has_detail>>>>>",has_detail)
                # print("has_deep>>>>>", has_deep)
                used_list = {
                    "index": {"temp": temp_index, "sheet": index_tab, "isDetail": is_detail,
                              "children": index_children},
                    "detail": {"temp": temp_detail, "sheet": detail_tab,
                               "isDetail": is_deep, "related": index_nm, "children": detail_children},
                    "deep": {"temp": temp_deep, "sheet": deep_tab, "related": deep_tab.get("parent"),
                             "isDetail": len(detail_children) > 0, "children": detail_children}
                }
                # request.app["used"] = {"table": index_tab, "prefix": val["url"], "tier": None}

                # checkUrlTier(request.path, val["url"], request.app["used"])
                tier = request.app["used"].get("tier")
                request.app["used"][tier] = used_list.get(tier)

                # request.app["pathsName"].append(val["title"])

                # if val.get("item") and len(val["item"]) > 0:
                #     for cval in val["item"]:
                #         checkUrlTier(request.path, cval["url"], request.app["used"])
                #         tier = request.app["used"].get("tier")
                #         request.app["used"][tier] = used.get(tier)
                #         request.path.startswith(cval["url"]) and request.app["pathsName"].append(cval["title"])
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

        @flaskApp.errorhandler(Exception)
        def error_other(error):
            """这个handler可以catch住所有的abort(500)和raise exeception."""
            response = dict(status=0, message="500 Error")
            if not filterPath(request):
                raise (error)
                print("other_error:", type(error), ">>>>>", error, request.path)
            return json.dumps({"success": False, "msg": "500-Error：" + str(error)}) if is_xhr(
                request) else render_template("templates/error.html", error=error)

    # 注意debug模式下只能在主线程中
    # app.run(host="0.0.0.0", debug=app.config["DEBUG"], port=app.config["PORT"])

from .const import Behavior, MODE, LOGIN, SUPER, RIGHTS, ADMIN
from libs.io import File, Json
import os
from libs.core import dater
dater().debug("---主程序运行：进行配置初始化！QQ---")

CONFIG = Json(("data", "config.json")).result
SHEETS = Json(("data", "sheets.json")).result
TEMPLATE = Json(("data", "template.json")).result
# 资源路径
assets = CONFIG.get("assets", {})
class ASSETS(Behavior):
    PATH = assets.get("path", "data")
    HOST = assets.get("host", "localhost")
    PORT = assets.get("port", 5000)
    STATICS = os.sep.join((assets.get("path", "data"), "statics"))
    TEMPLATE = os.sep.join((assets.get("path", "data"), "view"))
    DB = os.sep.join((assets.get("path", "data"), "db", assets.get("db", "ccs.db")))

# 上传路径
class UP(Behavior):
    IMAGE = (ASSETS.STATICS.val, "image")
    VIDEO = (ASSETS.STATICS.val, "video")
    AUDIO = (ASSETS.STATICS.val, "audio")
    OTHER = (ASSETS.STATICS.val, "other")

File.upPaths = {"image": UP.IMAGE.val, "video": UP.VIDEO.val, "audio": UP.AUDIO.val, "application": UP.OTHER.val}
print(">>>>>>>upPaths>>>>", File.upPaths)

TITLE = CONFIG.get("title", {"header": "", "subhead": "", "footer": ""})
PER_PAGE = 15
PATTERN = MODE.SINGLE.value
loginType = CONFIG.get("enter", "account")
loginType = loginType.upper() if isinstance(loginType, str) and hasattr(LOGIN, loginType.upper()) else "ACCOUNT"
ENTER = LOGIN[loginType].value
# 是否允许修改
CHANGE = False

# 白名单
IGNORE = ["/favicon.ico", "/statics", "/sign", "/api"]

TABLES = CONFIG.get("tables", [])
ROUTES = CONFIG.get("routes", {})
ASIDE = []
def prefix(key_item, route):
    url_prefix = route.get("url")
    url_prefix = url_prefix if isinstance(url_prefix, str) else "/" + key_item
    url_prefix = url_prefix if url_prefix.startswith("/") or url_prefix == "#" else "/" + url_prefix
    name = route.get("name", "_".join(url_prefix.split("/")[1:]))
    # print(">>>>>keyStr>>>>", _key)
    if key_item:
        route["key"] = key_item
    route["url"], route["name"] = url_prefix, name
    return url_prefix

def confirmSheet(_key, tables):
    table = tables.get(_key)
    if not table:
        table = tables.get("_")
        table = list(tables.values())[0] if not table else table
    return table

def confirmChildren(child):
    res = {}
    if isinstance(child, dict):
        _key = child.get("key", child.get("name"))
        child["key"] = _key
        res[_key] = child
    if isinstance(child, (list, tuple)):
        for k, v in enumerate(child): res.update(confirmChildren(v))
    return res

def createDeepHas(parent):
    hasDeep = {}
    for k, v in parent.items():
        children = v.get("deep", {})
        if children:
            deeps = confirmChildren(children)
            for _k_ in deeps:
                deep = deeps[_k_]
                # grandpa = v.get("parent")
                # deep["grandpa"] = "{0}.{1}".format(grandpa, k) if grandpa else k
                # grandpa = [g_v for g_v in v.get("grandpa", [])]
                deep["parent"] = k
                # grandpa.append(k)
                deep["grandpa"] = [g_v for g_v in v.get("grandpa", [])] + [k]

            grandchildren = createDeepHas(deeps)
            deeps.update(grandchildren)
            hasDeep.update(deeps)
    return hasDeep

for key_item in ROUTES:
    route = ROUTES[key_item]
    prefix(key_item, route)
    table = confirmSheet(key_item, TABLES)
    route["table"], detail = table, table.get("detail", False)

    detail = confirmChildren(detail)
    route["has_detail"] = detail
    route["has_deep"] = createDeepHas(detail)
    # for k, v in detail.items():
    #     deep = v.get("deep", {})
    #     if deep:
    #         deep = confirmChildren(deep)
    #         for _k_ in deep: deep[_k_]["parent"] = k
    #         route["has_deep"].update(deep)
    item = route.get("item", [])
    if len(item) > 0:
        for r in item:
            prefix(None, r)
    ASIDE.append(route)
INDEX_URL = ASIDE[0].get("url", "#")
INDEX_ITEM = ASIDE[0].get("item", [])
INDEX = INDEX_ITEM[0].get("url", INDEX_URL) if len(INDEX_ITEM) > 0 else INDEX_URL

# INDEX = "/intro"

from .const import Behavior, MODE, LOGIN, SUPER, RIGHTS, ADMIN
from libs.io import File, Json
import os

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

File.upPaths = {"image": UP.IMAGE.val, "video": UP.VIDEO.val, "audio": UP.AUDIO.val}
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

for key_item in ROUTES:
    route = ROUTES[key_item]
    url_prefix = prefix(key_item, route)
    item = route.get("item", [])
    if len(item) > 0:
        for r in item:
            prefix(None, r)
    # ASIDE.append({"title": route.get("title"), "href": route.get("href"), "url": url_prefix})
    ASIDE.append(route)
INDEX_URL = ASIDE[0].get("url", "#")
INDEX_ITEM = ASIDE[0].get("item", [])
INDEX = INDEX_ITEM[0].get("url", INDEX_URL) if len(INDEX_ITEM) > 0 else INDEX_URL

# INDEX = "/intro"

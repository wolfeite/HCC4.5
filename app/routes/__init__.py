# import sys
# print(">>>>>__file__", __file__, __name__, getattr(sys.modules["app.routes"],"filter","无"))
from . import api, common, filter, sign
# from libs.analyser.Config import Modules
# exec("from . import filter, api, sign, common")
# f = Modules(("data", "builder.json"))
# f.plugin(("app", "routes"))

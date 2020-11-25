from .pattern import ViewModel
from flask import request

def factoryDB(isDetail=False, **con):
    db = request.app.get("db")
    name = selectTable(isDetail).get("name")
    model = ViewModel(db, name, request, **con) if name else None
    # if tableUsed:
    #     if not isDetail:
    #         model = ViewModel(db, tableUsed.get("name", "screen"), request, **con)
    #     else:
    #         if "detail" in path and detail:
    #             model = ViewModel(db, detail.get("name", "detail"), request, **con)
    #         elif "deep" in path and deep:
    #             model = ViewModel(db, deep.get("name", "deep"), request, **con)

    # if len(tables) == 1:
    #     table = tables[0]
    #     if not isDetail:
    #         model = ViewModel(db, table.get("name", "screen"), request, **con)
    #     elif isDetail and tables[0].get("detail"):
    #         model = ViewModel(db, table.get("name", "detail"), request, **con)
    # else:
    #     pass
    return model

def getTable(name, **con):
    return ViewModel(request.app.get("db"), name, request, **con)

def selectTable(isDetail=False):
    table = request.app.get("used", {}).get("table")
    res, path, detail = {}, request.path, table.get("detail", {})
    if isDetail and "detail" in path:
        res = detail
    elif isDetail and "deep" in path:
        res = detail.get("deep", {})
    elif not isDetail:
        res = table
    return res

class Screen(ViewModel):
    def __init__(self, db, **con):
        super(Screen, self).__init__(db, "screen", request, **con)

class Detail(ViewModel):
    def __init__(self, db, **con):
        super(Detail, self).__init__(db, "detail", request, **con)

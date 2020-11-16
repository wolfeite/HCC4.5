from .pattern import ViewModel
from flask import request

def factoryDB(isDetail=False, **con):
    db, path, tableUsed = request.app.get("db"), request.path, request.app.get("used", {}).get("table")
    model, detail = None, tableUsed.get("detail")
    print(">>>>>>factoryDB>>", tableUsed)
    if tableUsed:
        if not isDetail:
            model = ViewModel(db, tableUsed.get("name", "screen"), request, **con)
        elif isDetail and detail:
            model = ViewModel(db, detail.get("name", "detail"), request, **con)

    # if len(tables) == 1:
    #     table = tables[0]
    #     if not isDetail:
    #         model = ViewModel(db, table.get("name", "screen"), request, **con)
    #     elif isDetail and tables[0].get("detail"):
    #         model = ViewModel(db, table.get("name", "detail"), request, **con)
    # else:
    #     pass
    return model

class Screen(ViewModel):
    def __init__(self, db, **con):
        super(Screen, self).__init__(db, "screen", request, **con)

class Detail(ViewModel):
    def __init__(self, db, **con):
        super(Detail, self).__init__(db, "detail", request, **con)

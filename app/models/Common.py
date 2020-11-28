from .pattern import ViewModel
from flask import request

def factoryDB(**con):
    name = getSheet().get("name")
    return getTable(name, **con) if name else None

def getTier():
    used = request.app.get("used")
    return used.get(used.get("tier"))

def getSheet():
    return getTier().get("sheet")

def getTable(name, **con):
    return ViewModel(request.app.get("db"), name, request, **con)

def getTemplate(path):
    return request.app["template"].get(path, {})

class Screen(ViewModel):
    def __init__(self, db, **con):
        super(Screen, self).__init__(db, "screen", request, **con)

class Detail(ViewModel):
    def __init__(self, db, **con):
        super(Detail, self).__init__(db, "detail", request, **con)

from libs.http import createFlaskApp
from app import config_app
import sys
from PyQt5.QtWidgets import QApplication
from gui import Gui
from libs.db import SqliteDb
from app.config import setting

if __name__ == "__main__":
    assets = setting.ASSETS
    assetsPath, host, port = assets.PATH.val, assets.HOST.val, assets.PORT.val
    gui = Gui()
    QApp = QApplication(sys.argv)
    gui.init(assetsPath)
    # db = SqliteDb(assetsPath + "/db/ccs.db")
    db = SqliteDb(assets.DB.val)
    # template_folder=assetsPath + "/view",static_folder=assetsPath + "/statics"
    httpApp = createFlaskApp({"host": host, "debug": False, "port": port}, template_folder=assets.TEMPLATE.val,
                             static_folder=assets.STATICS.val)
    httpApp.attr = ("gui", gui)
    httpApp.attr = ("db", db)
    config_app(httpApp)
    # import libs.io
    sys.exit(QApp.exec_())

from libs.http import createFlaskApp
from app import config_app
import sys
from PyQt5.QtWidgets import QApplication
from gui import Gui
from libs.db import SqliteDb
from app.config import setting

if __name__ == "__main__":
    assets = setting.ASSETS
    assetsPath = assets.PATH.val
    gui = Gui()
    QApp = QApplication(sys.argv)
    gui.init(assetsPath)
    # db = SqliteDb(assetsPath + "/db/ccs.db")
    db = SqliteDb(assets.DB.val)
    # template_folder=assetsPath + "/view",static_folder=assetsPath + "/statics"
    httpApp = createFlaskApp({"host": "0.0.0.0", "debug": False, "port": 5000}, template_folder=assets.TEMPLATE.val,
                             static_folder=assets.STATICS.val)
    httpApp.attr = ("gui", gui)
    httpApp.attr = ("db", db)
    config_app(httpApp)
    # import libs.io
    sys.exit(QApp.exec_())

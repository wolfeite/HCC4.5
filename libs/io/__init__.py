# Author: 骆琦（wolfeite）
# Corp: 朗迹
# StartTime:2020.7.21
# Version:1.0
from .File import File, Path
from .Json import Json
from .Loader import Loader
from libs.analyser.Config import Modules
f = Modules(("data", "builder.json"))
f.plugin(("libs", "io"))
import sys
config = getattr(sys.modules["libs.io"], "Config", None)
config and config.Config.test_imports()
# from .Office import Office
# from .Pdf import Pdf
# from .Video import Video
# from .Mp3 import Mp3

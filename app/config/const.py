from enum import Enum
import os

class Behavior(Enum):
    def __getitem__(self, key):
        return getattr(self, key)

    @property
    def val(self):
        # return (self.name, self.value)
        return self.value

    def __str__(self):
        return '{0}={1}'.format(self.name, self.value)

class MODE(Behavior):
    # multiple 0多场景模式，single 1单场景模式
    MULTIPLE = 0
    SINGLE = 1
    DEFAULT = 1

class RIGHTS(Behavior):
    ADMIN = 800
    SUPER = 1000
    DEFAULT = 100

class SUPER(Behavior):
    ID = 0
    NUMBER = 0
    NAME = "heroAge"
    PASSWORD = "123456"
    NICKNAME = "Administer"
    RANK = RIGHTS.SUPER.value
    THEME = "all"

# print("???>>>>", SUPER["rank"].val, SUPER.rank.val, SUPER.rank.value, type(SUPER["rank"].val))
class LOGIN(Behavior):
    FREE = 0
    AUTO = 1
    ACCOUNT = 2
    EMAIL = 3
    PHONE = 4

# # 资源路径
# class ASSETS(Behavior):
#     HOST = "localhost"
#     PORT = "5000"
#     STATICS = os.sep.join((ASSETS_PATH, "statics"))
#
# # 上传路径
# class UP(Behavior):
#     IMAGE = (ASSETS.STATICS.val, "image")
#     VIDEO = (ASSETS.STATICS.val, "video")
#     AUDIO = (ASSETS.STATICS.val, "audio")

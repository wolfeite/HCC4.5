import hashlib
from .pattern import ViewModel
from flask import request

class Account(ViewModel):
    rule = "wolfeite"
    def __init__(self, db, **con):
        super(Account, self).__init__(db, "account", request, **con)
        self._md5()

    def _md5(self):
        self.password = self.md5(self.password)

    @classmethod
    def md5(cls, pwd):
        if pwd:
            _md5 = pwd + cls.rule
            md5 = hashlib.md5()
            md5.update(_md5.encode(encoding='utf-8'))
            _md5 = md5.hexdigest()
            return _md5
        else:
            return pwd

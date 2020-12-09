from libs.io import Json, File
from libs.util import flat_dict, Plug, Path

class Modules():
    hiddenImports = ['pkg_resources.py2_warn']
    def __init__(self, path):
        res = Json(path).result
        self.json = res.get("modules", {})
        self.flat = flat_dict(self.json)
        self.parse()

    def parse(self):
        if not isinstance(self.flat, dict):
            return {}

        for k, v in self.flat.items():
            self.flat[k] = [v] if not isinstance(v, list) else v
            includes, exceptions = self.flat[k], []
            last = None if len(includes) == 0 else includes[-1]
            if isinstance(last, list):
                exceptions = includes.pop(-1)
            self.flat[k] = {"modules": includes, "exceptions": exceptions}

    @property
    def imports(self):
        # 配置文件中需要hiddenimports模块
        res = []
        print("flat>>>", self.flat)
        for k, v in self.flat.items():
            modules, exceptions = v.get("modules", []), v.get("exceptions", [])
            if modules:
                res += Plug(k, modules=modules, exceptions=exceptions).imports
            elif not modules and exceptions:
                res += Plug(k, exceptions=exceptions).imports
        return res + self.hiddenImports

    @classmethod
    def setImports(cls, val):
        val = val if isinstance(val, list) else [val]
        cls.hiddenImports += val

    def plugin(self, path, modules=[]):
        # 结合配置文件中的需求，导入指定路径下的模块
        self.setImports(modules)
        path = ".".join(path) if isinstance(path, (list, tuple)) else path
        flat = self.flat.get(path, {})
        Plug.into(path, flat.get("modules", []) + modules)

    def generate_spec(self):
        debug_str = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
modules = {0}

a = Analysis(['index.py'],
             pathex=['{1}'],
             binaries=[],
             datas=[],
             hiddenimports=modules,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='{2}',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console={3} , icon='icon.ico')

        '''
        File().write("index_debug.spec", debug_str.format(self.imports, Path().root, "index_debug", True))
        File().write("index.spec", debug_str.format(self.imports, Path().root, "index", False))

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
modules = ['libs.io.Config', 'pkg_resources.py2_warn']

a = Analysis(['index.py'],
             pathex=['E:\wolfeite\projectPy\heroage\EHCC5.0\data_controller_center\DCC4.5'],
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
          name='index_debug',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True , icon='icon.ico')

        
# -*- mode: python ; coding: utf-8 -*-

# Project folders
# data/
# src/
# main.ico
# main.spec
# readme.txt

block_cipher = None


a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[('src/', '.')],
    hiddenimports=['os',
                   're',
                   'vdf',
                   'yaml',
                   'winshell',
                   'glob',
                   'pathlib.Path',
                   'xml.dom.minidom',
                   'dataclasses.dataclass',
                   'dataclasses.field',
                   'win32com.client.Dispatch'
	],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Rom Detective',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=False,
	icon='main.ico',
)

import shutil
shutil.copyfile('readme.txt', '{0}/readme.txt'.format(DISTPATH))
shutil.copytree('data', '{0}/data'.format(DISTPATH))

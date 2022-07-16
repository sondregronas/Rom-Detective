# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[('src/', '.')],
    hiddenimports=[],
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

import os
import shutil

os.makedirs(os.path.dirname('{0}/logs/'.format(DISTPATH)), exist_ok=True)
os.makedirs(os.path.dirname('{0}/config/'.format(DISTPATH)), exist_ok=True)

shutil.copyfile('default_files/readme.txt', '{0}/readme.txt'.format(DISTPATH))

shutil.copyfile('default_files/logs/active_shortcuts.log', '{0}/logs/active_shortcuts.log'.format(DISTPATH))
shutil.copyfile('default_files/logs/blacklist.log', '{0}/logs/blacklist.log'.format(DISTPATH))
shutil.copyfile('default_files/logs/platforms.log', '{0}/logs/platforms.log'.format(DISTPATH))

shutil.copyfile('default_files/config/config.cfg', '{0}/config/config.cfg'.format(DISTPATH))
shutil.copyfile('default_files/config/whitelist.cfg', '{0}/config/whitelist.cfg'.format(DISTPATH))
shutil.copyfile('default_files/config/blacklist.cfg', '{0}/config/blacklist.cfg'.format(DISTPATH))

shutil.copytree('data', '{0}/data'.format(DISTPATH))

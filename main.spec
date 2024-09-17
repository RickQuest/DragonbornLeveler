# -*- mode: python ; coding: utf-8 -*-
import os
icon_path = os.path.abspath('gui/resources/icons/skyrim.ico')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('gui/resources', 'gui/resources'), ('core/assets','core/assets'), ('tests/assets','tests/assets')],
    hiddenimports=['comtypes', 'comtypes.stream','PyQt5.QtMultimedia', 'PyQt5.QtMultimediaWidgets'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
    excludedirectories=['tools', 'tests', '.vscode', '.github']
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DragonbornLeveler',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path
)

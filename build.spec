# -*- mode: python ; coding: utf-8 -*-
# Rename this file to build.spec before running: pyinstaller build.spec
import os
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('ui', 'ui'),
    ],
    hiddenimports=[
        'webview',
        'webview.platforms.winforms',
        'webview.platforms.edgechromium',
        'usb',
        'usb.core',
        'usb.util',
        'usb.backend',
        'usb.backend.libusb1',
        'serial',
        'serial.tools',
        'serial.tools.list_ports',
        'Crypto',
        'Crypto.Cipher',
        'Crypto.Hash',
        'colorama',
        'clr',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PySide6', 'PyQt5', 'PyQt6', 'tkinter', 'matplotlib'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MTK Studio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='ui/assets/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MTK Studio',
)

"""MTK Studio -- PyInstaller build script."""
import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--name=MTK Studio',
    '--windowed',
    '--onedir',
    '--add-data=ui:ui',
    '--hidden-import=webview',
    '--hidden-import=usb',
    '--hidden-import=serial',
    '--hidden-import=Crypto',
    '--hidden-import=colorama',
    '--icon=ui/assets/icon.ico',
    '--clean',
    '--noconfirm',
])

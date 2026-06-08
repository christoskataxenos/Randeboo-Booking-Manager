# -*- mode: python ; coding: utf-8 -*-


from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Συλλογή όλων των submodules της βιβλιοθήκης holidays για να συμπεριληφθούν στο executable
hidden_imports_holidays = collect_submodules('holidays')
datas_holidays = collect_data_files('holidays')

a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('src/randeboo.ico', '.'), ('src/randeboo.png', '.')] + datas_holidays,
    hiddenimports=hidden_imports_holidays,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='RandeBoo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['src\\randeboo.ico'],
)

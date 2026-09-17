# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, copy_metadata

datas=[]; binaries=[]; hiddenimports=[]
ttk_datas, ttk_binaries, ttk_hiddenimports = collect_all("ttkbootstrap")
datas += ttk_datas; binaries += ttk_binaries; hiddenimports += ttk_hiddenimports
locales_dir = Path("src/art_timelapse/locales")
if locales_dir.exists():
    datas.append((str(locales_dir), "art_timelapse/locales"))
try:
    datas += copy_metadata("art-timelapse")
except Exception:
    pass

a=Analysis(["pyinstaller_main.py"], pathex=["src"], binaries=binaries, datas=datas, hiddenimports=hiddenimports, hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False, optimize=0)
pyz=PYZ(a.pure)
exe=EXE(pyz, a.scripts, [], exclude_binaries=True, name="art-timelapse", debug=False, bootloader_ignore_signals=False, strip=False, upx=True, console=False, disable_windowed_traceback=False, argv_emulation=False, target_arch=None, codesign_identity=None, entitlements_file=None)
coll=COLLECT(exe, a.binaries, a.datas, strip=False, upx=True, upx_exclude=[], name="art-timelapse")

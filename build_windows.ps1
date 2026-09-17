$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
Write-Host "== Art Timelapse: build portable de Windows =="
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "dist")  { Remove-Item "dist"  -Recurse -Force }
if (Test-Path "venv")  { Remove-Item "venv"  -Recurse -Force }
if (Get-Command py -ErrorAction SilentlyContinue) { & py -3.14 -m venv venv }
elseif (Get-Command python -ErrorAction SilentlyContinue) { python -c "import sys; assert sys.version_info >= (3,14), 'Se requiere Python 3.14 o superior'"; python -m venv venv }
else { throw "No se encontro Python 3.14." }
$PY = Join-Path $Root "venv\Scripts\python.exe"
& $PY --version
& $PY -m ensurepip --upgrade
& $PY -m pip install --upgrade pip setuptools wheel
& $PY -m pip install -e ".[dev]"
& $PY -m pip install setuptools-gettext translate-toolkit
& $PY build_locales.py
if (-not (Test-Path "src\art_timelapse\locales")) { throw "No se genero src\art_timelapse\locales" }
& $PY -m PyInstaller --clean --noconfirm art_timelapse.spec
$VERSION = & $PY -c "from importlib.metadata import version; print(version('art-timelapse'), end='')"
$ZIP = "art-timelapse-windows-portable-v$VERSION.zip"
if (Test-Path $ZIP) { Remove-Item $ZIP -Force }
tar -c -a -f $ZIP -C dist art-timelapse
Write-Host "Build terminada: $Root\$ZIP"
Write-Host "Ejecutable: $Root\dist\art-timelapse\art-timelapse.exe"

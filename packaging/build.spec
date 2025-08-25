# packaging/build.spec
# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

project_root = Path(__file__).resolve().parents[1]
pathex = [str(project_root)]

datas = []
datas += collect_data_files("app", includes=["templates/**", "templates/*.html"])

static_dir = project_root / "static"
if static_dir.exists():
    for p in static_dir.rglob("*"):
        if p.is_file():
            datas.append((str(p), "static"))

config_sample = project_root / "config" / "app.env.sample"
if config_sample.exists():
    datas.append((str(config_sample), "config"))

a = Analysis(
    ["app/main.py"],
    pathex=pathex,
    binaries=[],
    datas=datas,
    hiddenimports=[
        "jinja2.ext",
        "jinja2.loaders",
        "app.routes.clients",
        "app.routes.trips",
        "app.routes.bookings",
        "app.routes.home",
        "app.services.dedupe",
        "app.services.audit",
        "app.services.backups",
        "app.services.sync",
        "sqlalchemy.dialects.sqlite",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Astraion",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Astraion",
)

app = BUNDLE(coll)

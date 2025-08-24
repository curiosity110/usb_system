# -*- mode: python ; coding: utf-8 -*-

"""PyInstaller spec for one-file Astraion executable.

This configuration bundles the FastAPI templates and static assets and
directs PyInstaller to use a local ``logs`` directory for its runtime
extraction and logging.
"""

import os

block_cipher = None

# Data files: include Jinja templates and static assets.
datas = [
    ("app/templates", "app/templates"),
    ("static", "static"),
]

# Ensure a logs directory exists alongside the executable.
if not os.path.exists("logs"):
    os.makedirs("logs")

a = Analysis(
    ["app/main.py"],
    pathex=[],
    binaries=[],
    datas=datas,
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
    name="Astraion",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir="logs",
    console=True,
    icon=None,
)


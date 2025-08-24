# PyInstaller spec file for Astraion Travel
block_cipher = None

import sys
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('rapidfuzz')

a = Analysis(['app/main.py'], pathex=['.'], hiddenimports=hiddenimports)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Astraion',
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
    name='Astraion',
)

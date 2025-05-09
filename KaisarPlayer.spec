# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('icons', 'icons'),
        ('languages', 'languages'),
        ('Data/Emotion_Data', 'Data/Emotion_Data')
    ],
    hiddenimports=[
        'camera_manager',
        'ui',
        'player',
        'playlist',
        'history',
        'settings',
        'emotion_manager',
        'language_manager',
        'path_utils',
        'cv2',
        'numpy',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk'
    ] + collect_submodules('customtkinter') + collect_submodules('darkdetect'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='KaisarPlayer',
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
    entitlements_file=None
)
# -*- mode: python ; coding: utf-8 -*-
# PyInstaller Spec File for Star Wars Legion Game Companion & AI Simulator
# GitHub Actions compatible version - runs from repository root

block_cipher = None

a = Analysis(
    ['MainMenu.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('utilities', 'utilities'),
        ('db', 'db'),
        ('bilder', 'bilder'),
        ('README.md', '.'),
        ('MainMenu.py', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'json',
        'logging',
        'subprocess',
        'random',
        'google',
        'google.ai',
        'google.genai',
        'google.generativeai',
        'google.api_core',
        'google.auth',
        'threading',
        'cv2',
        'uuid',
        'requests',
        'os',
        'sys',
        'utilities.LegionData',
        'utilities.LegionRules',
        'utilities.LegionUtils',
        'utilities.GameCompanion',
        'utilities.CustomFactoryMenu',
        'utilities.ArmeeBuilder',
        'utilities.BattlefieldMapCreator',
        'utilities.CardPrinter',
        'utilities.CustomBattleCardCreator',
        'utilities.CustomCommandCardCreator',
        'utilities.CustomUnitCreator',
        'utilities.CustomUpgradeCreator',
        'utilities.MissionBuilder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'gemini_key.txt',
    ],
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
    name='SWLegion',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='bilder/SW_legion_logo.ico',  # Use .ico file for Windows executables
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SWLegion',
)
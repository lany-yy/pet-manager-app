# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# 获取当前文件目录
current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.insert(0, current_dir)

# 收集所有需要打包的资源文件
datas = []

# 添加 kv 文件
kv_dir = os.path.join(current_dir, 'kv')
if os.path.exists(kv_dir):
    for filename in os.listdir(kv_dir):
        if filename.endswith('.kv'):
            datas.append((os.path.join(kv_dir, filename), 'kv'))

# 添加图标文件
icons_dir = os.path.join(current_dir, 'icons')
if os.path.exists(icons_dir):
    for filename in os.listdir(icons_dir):
        if filename.endswith('.png'):
            datas.append((os.path.join(icons_dir, filename), 'icons'))

# 添加数据库文件（可选，运行时会自动创建）
db_file = os.path.join(current_dir, 'pet_manager.db')
if os.path.exists(db_file):
    datas.append((db_file, '.'))

# 隐藏导入（确保所有依赖都被正确包含）
hiddenimports = [
    'kivy',
    'kivy.uix.screenmanager',
    'kivy.uix.popup',
    'kivy.uix.boxlayout',
    'kivy.uix.label',
    'kivy.uix.button',
    'kivy.uix.textinput',
    'kivy.uix.spinner',
    'kivy.uix.image',
    'kivy.uix.scrollview',
    'kivy.uix.gridlayout',
    'kivy.uix.relativelayout',
    'kivy.lang',
    'kivy.app',
    'kivy.clock',
    'kivy.properties',
    'plyer',
    'matplotlib',
    'matplotlib.backends.backend_tkagg',
    'PIL',
    'sqlite3',
    'hashlib',
    'datetime',
    'services.user_service',
    'services.pet_service',
    'services.vaccine_service',
    'services.weight_service',
    'services.reminder_service',
    'services.deworm_service',
    'services.stats_service',
    'services.feeding_service',
    'models.user',
    'models.pet',
    'models.vaccine',
    'models.weight',
    'models.reminder',
    'models.deworm',
    'models.feeding',
    'database.db_manager',
    'database.db_helper',
    'utils.date_helper',
    'utils.image_helper',
    'widgets.pet_card',
    'widgets.confirm_dialog',
    'widgets.chart_view',
    'screens.daily_screen',
    'screens.health_screens',
    'screens.settings_screen',
    'screens.statistics_screen'
]

a = Analysis(
    ['main.py'],
    pathex=[current_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PetManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 无控制台窗口，GUI程序
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可添加图标文件
)

# 创建单文件夹模式的输出
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PetManager'
)
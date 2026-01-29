"""
Setup.py для сборки macOS приложения с помощью py2app
Поддерживает как Intel (x86_64), так и Apple Silicon (arm64)
"""

from setuptools import setup
import sys
import platform

# Определяем архитектуру процессора
ARCH = platform.machine()
IS_ARM64 = ARCH == 'arm64'
IS_X86_64 = ARCH == 'x86_64'

# Определяем минимальную версию macOS для Apple Silicon
PYTHON_VERSION = sys.version_info[:2]
IS_PYTHON_313_PLUS = PYTHON_VERSION >= (3, 13)

# Настройки приложения
APP = ['main.py']
APP_NAME = 'CarSelection'
DATA_FILES = [
    ('', ['config.py']),  # Включаем config.py в bundle
]

# Опции для py2app
OPTIONS = {
    'argv_emulation': False,
    'strip': True,
    'optimize': 2,
    'includes': [
        'mysql.connector',
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'database',
        'expert_system',
    ],
    'packages': [
        'mysql',
        'mysql.connector',
        'PyQt6',
    ],
    'excludes': [
        'tkinter',  # Не используем tkinter, исключаем для уменьшения размера
    ],
    'resources': [],
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleGetInfoString': "Car Selection Application",
        'CFBundleIdentifier': "com.carselection.app",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',  # macOS High Sierra и выше
        'NSRequiresAquaSystemAppearance': False,
    },
}

# Для Python 3.13+ используем semi_standalone для избежания проблем
# Для Apple Silicon рекомендуется использовать alias режим
if IS_PYTHON_313_PLUS:
    if IS_ARM64:
        # Для Apple Silicon с Python 3.13+ используем alias режим
        OPTIONS['semi_standalone'] = False
        OPTIONS['alias'] = True
        print("⚠ Python 3.13+ на Apple Silicon обнаружен - используется alias режим")
    else:
        # Для Intel с Python 3.13+ используем semi_standalone
        OPTIONS['semi_standalone'] = True
        OPTIONS['alias'] = False
        print("⚠ Python 3.13+ на Intel обнаружен - используется semi_standalone режим")
else:
    # Для Python < 3.13 используем стандартный режим
    OPTIONS['semi_standalone'] = False
    OPTIONS['alias'] = False

# Для Apple Silicon добавляем специфичные настройки
if IS_ARM64:
    # Убеждаемся, что приложение компилируется для arm64
    OPTIONS['arch'] = 'arm64'
    print("✓ Настройка для Apple Silicon (arm64)")
elif IS_X86_64:
    OPTIONS['arch'] = 'x86_64'
    print("✓ Настройка для Intel (x86_64)")

setup(
    name=APP_NAME,
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'PyQt6>=6.7.0',
        'mysql-connector-python>=8.2.0',
    ],
)


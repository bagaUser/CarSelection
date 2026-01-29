"""
Setup script для сборки macOS приложения с помощью cx_Freeze
Поддерживает Apple Silicon (arm64) и Intel (x86_64)
Использует SQLAlchemy + SQLite - не требует внешних библиотек!
"""

import sys
import platform
from cx_Freeze import setup, Executable

# Определяем архитектуру
ARCH = platform.machine()
IS_ARM64 = ARCH == 'arm64'
IS_X86_64 = ARCH == 'x86_64'

print(f"Архитектура процессора: {ARCH}")

# Базовые опции сборки
build_exe_options = {
    "packages": [
        "PyQt6",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "sqlalchemy",
        "sqlalchemy.engine",
        "sqlalchemy.pool",
        "sqlalchemy.sql",
    ],
    "includes": [
        "database",
        "expert_system",
        "sqlite3",  # SQLite встроен в Python
    ],
    "excludes": [
        "tkinter",
        "unittest",
        "email",
        "http",
        "urllib",
        "xml",
        "pydoc",
    ],
    "include_files": [
        ("config.py", "config.py"),
    ],
    "optimize": 2,
}

# Настройки для macOS
if sys.platform == "darwin":
    if IS_ARM64:
        print("✓ Настройка для Apple Silicon (arm64)")
    elif IS_X86_64:
        print("✓ Настройка для Intel (x86_64)")

executable = Executable(
    script="main.py",
    base=None,
    target_name="CarSelection",
    icon=None,
)

setup(
    name="CarSelection",
    version="1.0.0",
    description="Экспертная система выбора автомобиля",
    author="Bogdan",
    options={
        "build_exe": build_exe_options,
    },
    executables=[executable],
)

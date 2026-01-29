#!/bin/bash

# Скрипт для сборки macOS приложения из Python скрипта
# Использует PyInstaller для создания .app bundle

echo "=========================================="
echo "Сборка macOS приложения"
echo "=========================================="

# Проверка наличия PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller не найден. Устанавливаю..."
    pip install pyinstaller
fi

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python3 не найден!"
    exit 1
fi

echo ""
echo "Шаг 1: Очистка предыдущих сборок..."
rm -rf build dist CarSelection.app

echo ""
echo "Шаг 2: Сборка приложения..."
# Проверка архитектуры для правильной сборки
ARCH=$(uname -m)
echo ""
echo "Обнаружена архитектура процессора: $ARCH"

if [ "$ARCH" = "arm64" ]; then
    echo "✓ Apple Silicon (M1/M2/M3) обнаружен - применяются оптимизации для ARM64"
elif [ "$ARCH" = "x86_64" ]; then
    echo "✓ Intel процессор обнаружен - применяются настройки для x86_64"
fi

pyinstaller --name="CarSelection" \
            --windowed \
            --onedir \
            --icon=NONE \
            --add-data="config.py:." \
            --hidden-import=mysql.connector \
            --hidden-import=PyQt6 \
            --hidden-import=PyQt6.QtCore \
            --hidden-import=PyQt6.QtGui \
            --hidden-import=PyQt6.QtWidgets \
            --hidden-import=database \
            --hidden-import=expert_system \
            --collect-all=mysql.connector \
            --collect-submodules=PyQt6 \
            --osx-bundle-identifier="com.carselection.app" \
            main.py

if [ $? -ne 0 ]; then
    echo "Ошибка при сборке!"
    exit 1
fi

echo ""
echo "Шаг 3: Перемещение .app bundle..."
if [ -d "dist/CarSelection.app" ]; then
    mv dist/CarSelection.app .
    echo "✓ Приложение создано: CarSelection.app"
else
    echo "Ошибка: .app bundle не найден в dist/"
    exit 1
fi

echo ""
echo "=========================================="
echo "Сборка завершена успешно!"
echo "=========================================="
echo ""
echo "Приложение находится в: CarSelection.app"
echo ""
echo "Для запуска:"
echo "  open CarSelection.app"
echo ""
echo "Для распространения:"
echo "  1. Создайте архив: zip -r CarSelection.zip CarSelection.app"
echo "  2. Или создайте DMG образ (требуются дополнительные инструменты)"
echo ""


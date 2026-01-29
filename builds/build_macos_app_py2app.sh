#!/bin/bash

# Скрипт для сборки macOS приложения из Python скрипта
# Использует py2app для создания .app bundle

echo "=========================================="
echo "Сборка macOS приложения (py2app)"
echo "=========================================="

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python3 не найден!"
    exit 1
fi

# Проверка наличия py2app
if ! python3 -c "import py2app" 2>/dev/null; then
    echo "py2app не найден. Устанавливаю..."
    pip3 install py2app
fi

echo ""
echo "Шаг 1: Очистка предыдущих сборок..."
rm -rf build dist CarSelection.app

# Проверка архитектуры
ARCH=$(uname -m)
echo ""
echo "Обнаружена архитектура процессора: $ARCH"

if [ "$ARCH" = "arm64" ]; then
    echo "✓ Apple Silicon (M1/M2/M3) обнаружен - применяются оптимизации для ARM64"
elif [ "$ARCH" = "x86_64" ]; then
    echo "✓ Intel процессор обнаружен - применяются настройки для x86_64"
fi

echo ""
echo "Шаг 2: Проверка зависимостей..."

# Проверка MySQL connector для правильной архитектуры
if python3 -c "import mysql.connector" 2>/dev/null; then
    echo "✓ mysql-connector-python установлен"
    # Проверяем архитектуру библиотеки
    MYSQL_ARCH=$(python3 -c "import mysql.connector; import platform; print(platform.machine())" 2>/dev/null)
    if [ "$MYSQL_ARCH" != "$ARCH" ]; then
        echo "⚠️  ВНИМАНИЕ: Архитектура MySQL connector может не совпадать!"
        echo "   Рекомендуется переустановить: pip3 install --force-reinstall --no-cache-dir mysql-connector-python"
    fi
else
    echo "⚠️  mysql-connector-python не найден, устанавливаю..."
    pip3 install mysql-connector-python
fi

echo ""
echo "Шаг 3: Сборка приложения с py2app..."

# Проверка версии Python для предупреждений
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Версия Python: $PYTHON_VERSION"

# Если Python 3.13+, используем специальный режим
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 13) else 1)" 2>/dev/null; then
    if [ "$ARCH" = "arm64" ]; then
        echo "⚠ Python 3.13+ на Apple Silicon обнаружен - используется alias режим в setup.py"
    else
        echo "⚠ Python 3.13+ обнаружен - используется semi_standalone режим в setup.py"
    fi
    echo "   Это нормально для избежания проблем с упаковкой стандартной библиотеки"
fi

# Проверка наличия setup.py
if [ ! -f "setup.py" ]; then
    echo "Ошибка: setup.py не найден!"
    echo "Файл setup.py необходим для сборки с py2app"
    exit 1
fi

# Проверка PyQt6 для Apple Silicon
if [ "$ARCH" = "arm64" ]; then
    echo ""
    echo "Проверка PyQt6 для Apple Silicon..."
    PYQT6_CHECK=$(python3 -c "import PyQt6; print('OK')" 2>&1)
    if [ "$PYQT6_CHECK" != "OK" ]; then
        echo "⚠️  ВНИМАНИЕ: PyQt6 может не работать правильно на Apple Silicon"
        echo "   Убедитесь, что PyQt6 установлен для ARM64:"
        echo "   pip3 install --force-reinstall --no-cache-dir PyQt6"
    fi
fi

echo ""
echo "Шаг 4: Сборка приложения с py2app..."

python3 setup.py py2app

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

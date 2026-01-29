#!/bin/bash

# Скрипт для сборки macOS приложения с помощью Nuitka
# Компилирует Python в нативный код - лучшая производительность

echo "=========================================="
echo "Сборка macOS приложения (Nuitka)"
echo "=========================================="

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python3 не найден!"
    exit 1
fi

# Проверка наличия nuitka
if ! python3 -c "import nuitka" 2>/dev/null; then
    echo "Nuitka не найден. Устанавливаю..."
    pip3 install nuitka
fi

# Проверка компилятора
if ! command -v clang &> /dev/null; then
    echo "⚠ Компилятор C не найден. Устанавливаю Xcode Command Line Tools..."
    xcode-select --install
    echo "Подождите установки и запустите скрипт снова"
    exit 1
fi

# Проверка архитектуры
ARCH=$(uname -m)
echo ""
echo "Обнаружена архитектура процессора: $ARCH"

if [ "$ARCH" = "arm64" ]; then
    echo "✓ Apple Silicon (M1/M2/M3) обнаружен"
    ARCH_FLAG="--macos-create-app-bundle"
elif [ "$ARCH" = "x86_64" ]; then
    echo "✓ Intel процессор обнаружен"
    ARCH_FLAG="--macos-create-app-bundle"
else
    ARCH_FLAG="--macos-create-app-bundle"
fi

echo ""
echo "Шаг 1: Очистка предыдущих сборок..."
rm -rf build CarSelection.app CarSelection.dist

echo ""
echo "Шаг 2: Сборка приложения с Nuitka..."
python3 -m nuitka \
    --standalone \
    --onefile \
    --macos-create-app-bundle=CarSelection.app \
    --macos-app-icon=NONE \
    --enable-plugin=pyqt6 \
    --include-module=mysql.connector \
    --include-module=database \
    --include-module=expert_system \
    --include-data-file=config.py=config.py \
    --macos-app-name="CarSelection" \
    --macos-app-mode=ui-element \
    --output-dir=. \
    --output-filename=CarSelection \
    main.py

if [ $? -ne 0 ]; then
    echo "Ошибка при сборке!"
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

#!/bin/bash

# Скрипт для сборки macOS приложения с помощью Briefcase (BeeWare)
# Отличная поддержка Python 3.13+ и Apple Silicon

echo "=========================================="
echo "Сборка macOS приложения (Briefcase)"
echo "=========================================="

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python3 не найден!"
    exit 1
fi

# Проверка наличия briefcase
if ! python3 -c "import briefcase" 2>/dev/null; then
    echo "Briefcase не найден. Устанавливаю..."
    pip3 install briefcase
fi

# Проверка архитектуры
ARCH=$(uname -m)
echo ""
echo "Обнаружена архитектура процессора: $ARCH"

if [ "$ARCH" = "arm64" ]; then
    echo "✓ Apple Silicon (M1/M2/M3) обнаружен"
elif [ "$ARCH" = "x86_64" ]; then
    echo "✓ Intel процессор обнаружен"
fi

echo ""
echo "Шаг 1: Инициализация проекта Briefcase..."

# Проверяем, инициализирован ли проект
if [ ! -f "pyproject.toml" ]; then
    echo "pyproject.toml не найден. Инициализирую проект..."
    # Используем существующий pyproject.toml или создаем новый
    if [ ! -f "pyproject.toml" ]; then
        echo "Создайте pyproject.toml вручную или используйте:"
        echo "  briefcase new"
        exit 1
    fi
fi

# Проверяем, есть ли секция [tool.briefcase]
if ! grep -q "\[tool.briefcase" pyproject.toml 2>/dev/null; then
    echo "⚠ pyproject.toml не содержит конфигурацию Briefcase"
    echo "Добавьте конфигурацию из примера в ALTERNATIVES.md"
    exit 1
fi

echo ""
echo "Шаг 2: Обновление зависимостей..."
briefcase update

echo ""
echo "Шаг 3: Сборка приложения для macOS..."
briefcase build macOS

if [ $? -ne 0 ]; then
    echo "Ошибка при сборке!"
    exit 1
fi

echo ""
echo "=========================================="
echo "Сборка завершена успешно!"
echo "=========================================="
echo ""
echo "Приложение находится в: macOS/app/CarSelection/CarSelection.app"
echo ""
echo "Для запуска:"
echo "  briefcase run macOS"
echo ""
echo "Для создания DMG для распространения:"
echo "  briefcase package macOS"
echo ""

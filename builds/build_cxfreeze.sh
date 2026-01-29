#!/bin/bash

# Скрипт для сборки macOS приложения с помощью cx_Freeze
# Альтернатива py2app с лучшей поддержкой Python 3.13+

echo "=========================================="
echo "Сборка macOS приложения (cx_Freeze)"
echo "=========================================="

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python3 не найден!"
    exit 1
fi

# Проверка наличия cx_Freeze
if ! python3 -c "import cx_Freeze" 2>/dev/null; then
    echo "cx_Freeze не найден. Устанавливаю..."
    pip3 install cx_Freeze
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
echo "Шаг 1: Очистка предыдущих сборок..."
rm -rf build dist

echo ""
echo "Шаг 2: Сборка приложения с cx_Freeze..."
python3 setup_cxfreeze.py build

if [ $? -ne 0 ]; then
    echo "Ошибка при сборке!"
    exit 1
fi

echo ""
echo "Шаг 3: Создание .app bundle..."
# cx_Freeze создает исполняемый файл, нужно обернуть в .app bundle
BUILD_DIR=$(find build -name "exe.macosx-*" -type d | head -1)

if [ -n "$BUILD_DIR" ] && [ -f "$BUILD_DIR/CarSelection" ]; then
    mkdir -p CarSelection.app/Contents/MacOS
    mkdir -p CarSelection.app/Contents/Resources
    cp "$BUILD_DIR/CarSelection" CarSelection.app/Contents/MacOS/
    chmod +x CarSelection.app/Contents/MacOS/CarSelection
    cp -r "$BUILD_DIR"/* CarSelection.app/Contents/Resources/ 2>/dev/null || true
    
    # Копируем cars.db, если существует
    if [ -f "cars.db" ]; then
        cp cars.db CarSelection.app/Contents/Resources/
        echo "✓ База данных cars.db включена в сборку"
    else
        echo "⚠ cars.db не найден - будет создан при первом запуске"
    fi
    
    # Создание Info.plist
    cat > CarSelection.app/Contents/Info.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>CarSelection</string>
    <key>CFBundleIdentifier</key>
    <string>com.carselection.app</string>
    <key>CFBundleName</key>
    <string>CarSelection</string>
    <key>CFBundleDisplayName</key>
    <string>Экспертная система выбора автомобиля</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF
    
    # Удаляем атрибуты безопасности для macOS Sequoia
    xattr -cr CarSelection.app 2>/dev/null || true
    
    echo "✓ Приложение создано: CarSelection.app"
else
    echo "⚠ Исполняемый файл не найден в ожидаемом месте"
    echo "Проверьте папку build/"
    if [ -n "$BUILD_DIR" ]; then
        echo "Найдена директория: $BUILD_DIR"
        ls -la "$BUILD_DIR" | head -10
    fi
    exit 1
fi

echo ""
echo "=========================================="
echo "Сборка завершена!"
echo "=========================================="
echo ""
echo "Приложение находится в: CarSelection.app"
echo ""
echo "Для запуска:"
echo "  open CarSelection.app"
echo ""

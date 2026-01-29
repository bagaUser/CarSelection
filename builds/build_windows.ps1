# Скрипт для сборки Windows приложения из Python скрипта
# Использует PyInstaller для создания исполняемого файла

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Сборка Windows приложения" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Проверка наличия Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python обнаружен: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Ошибка: Python не найден!" -ForegroundColor Red
    Write-Host "Убедитесь, что Python установлен и добавлен в PATH" -ForegroundColor Yellow
    exit 1
}

# Проверка наличия PyInstaller
try {
    $null = pyinstaller --version 2>&1
    Write-Host "PyInstaller обнаружен" -ForegroundColor Green
} catch {
    Write-Host "PyInstaller не найден. Устанавливаю..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Переход в корневую директорию проекта
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location $projectRoot

Write-Host ""
Write-Host "Шаг 1: Очистка предыдущих сборок..." -ForegroundColor Yellow

# Очистка старых сборок
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}
if (Test-Path "CarSelection.spec") {
    Remove-Item -Force "CarSelection.spec"
}

Write-Host ""
Write-Host "Шаг 2: Проверка зависимостей..." -ForegroundColor Yellow

# Проверка PyQt6
try {
    python -c "import PyQt6" 2>&1 | Out-Null
    Write-Host "✓ PyQt6 установлен" -ForegroundColor Green
} catch {
    Write-Host "⚠ PyQt6 не найден, устанавливаю..." -ForegroundColor Yellow
    pip install PyQt6
}

# Проверка SQLAlchemy
try {
    python -c "import sqlalchemy" 2>&1 | Out-Null
    Write-Host "✓ SQLAlchemy установлен" -ForegroundColor Green
} catch {
    Write-Host "⚠ SQLAlchemy не найден, устанавливаю..." -ForegroundColor Yellow
    pip install SQLAlchemy
}

Write-Host ""
Write-Host "Шаг 3: Сборка приложения..." -ForegroundColor Yellow

# Создание директории для сборки
$buildDir = Join-Path $projectRoot "builds" "windows_build"
if (-not (Test-Path $buildDir)) {
    New-Item -ItemType Directory -Path $buildDir | Out-Null
}

# Сборка приложения с PyInstaller
pyinstaller --name="CarSelection" `
            --windowed `
            --onefile `
            --add-data="config.py;." `
            --hidden-import=sqlalchemy `
            --hidden-import=sqlalchemy.engine `
            --hidden-import=sqlalchemy.pool `
            --hidden-import=sqlalchemy.sql `
            --hidden-import=sqlite3 `
            --hidden-import=PyQt6 `
            --hidden-import=PyQt6.QtCore `
            --hidden-import=PyQt6.QtGui `
            --hidden-import=PyQt6.QtWidgets `
            --hidden-import=database `
            --hidden-import=expert_system `
            --collect-submodules=PyQt6 `
            --collect-submodules=sqlalchemy `
            --icon=NONE `
            --noconsole `
            main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Ошибка при сборке!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Шаг 4: Перемещение файлов в builds..." -ForegroundColor Yellow

# Копирование собранного файла в builds
if (Test-Path "dist\CarSelection.exe") {
    Copy-Item "dist\CarSelection.exe" -Destination $buildDir -Force
    Write-Host "✓ Приложение создано: $buildDir\CarSelection.exe" -ForegroundColor Green
} else {
    Write-Host "Ошибка: CarSelection.exe не найден в dist/" -ForegroundColor Red
    exit 1
}

# Копирование config.py в папку сборки (если нужно)
if (Test-Path "config.py") {
    Copy-Item "config.py" -Destination $buildDir -Force
    Write-Host "✓ config.py скопирован в папку сборки" -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Сборка завершена успешно!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Приложение находится в: $buildDir\CarSelection.exe" -ForegroundColor Green
Write-Host ""
Write-Host "Для распространения:" -ForegroundColor Yellow
Write-Host "  1. Скопируйте папку $buildDir полностью" -ForegroundColor White
Write-Host "  2. База данных SQLite (cars.db) будет создана автоматически при первом запуске" -ForegroundColor White
Write-Host "  3. Никаких дополнительных настроек не требуется" -ForegroundColor White
Write-Host ""


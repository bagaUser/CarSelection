# Инструкция по сборке Windows приложения

## ✅ Статус

Приложение успешно переведено на **SQLAlchemy + SQLite** вместо MySQL.

## 📦 Зависимости

Все зависимости указаны в `requirements.txt`:
- PyQt6 (GUI)
- SQLAlchemy (ORM для работы с базой данных)
- SQLite (встроен в Python, не требует установки)

## 🔨 Сборка приложения

### Вариант 1: Использование скрипта (рекомендуется)

```powershell
# Запустите скрипт сборки
.\builds\build_windows.ps1
```

### Вариант 2: Ручная сборка

```powershell
# Установите PyInstaller (если еще не установлен)
pip install pyinstaller

# Очистите предыдущие сборки
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force CarSelection.spec -ErrorAction SilentlyContinue

# Запустите сборку
python -m PyInstaller --name="CarSelection" `
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
    --noconsole `
    main.py

# Скопируйте файлы в папку сборки
New-Item -ItemType Directory -Path "builds\windows_build" -Force | Out-Null
Copy-Item "dist\CarSelection.exe" -Destination "builds\windows_build\" -Force
Copy-Item "config.py" -Destination "builds\windows_build\" -Force
```

## 📁 Результат сборки

После сборки приложение будет находиться в:
```
builds\windows_build\CarSelection.exe
```

## 🚀 Использование

1. **Запустите** `CarSelection.exe`
2. **База данных** SQLite (`cars.db`) будет создана автоматически при первом запуске в той же директории, где находится исполняемый файл
3. **Никаких дополнительных настроек не требуется!**

## ✨ Преимущества SQLAlchemy + SQLite

- ✅ Нет внешних зависимостей (не нужен MySQL Server)
- ✅ Простая сборка (все включено в один .exe файл)
- ✅ Портативность (один файл базы данных)
- ✅ Не требует сервера
- ✅ Быстрая работа для небольших баз данных
- ✅ Автоматическое создание базы данных при первом запуске

## 🔍 Просмотр базы данных в Cursor

Для просмотра файлов `.db` в Cursor установите одно из рекомендуемых расширений:
- **SQLite Viewer** (`qwtel.sqlite-viewer`)
- **SQLite** (`alexcvzz.vscode-sqlite`)
- **SQLTools + SQLite Driver** (`mtxr.sqltools` и `mtxr.sqltools-driver-sqlite`)

Подробнее см. `.vscode/README_DB_VIEWER.md`

## 📝 Примечания

- Приложение собрано как один исполняемый файл (`--onefile`)
- Консольное окно скрыто (`--noconsole`)
- База данных создается автоматически при первом запуске
- Все данные хранятся локально в файле `cars.db`

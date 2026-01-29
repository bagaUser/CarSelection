# Сборка приложения для macOS

## ⚡ Быстрое решение для Apple Silicon (M1/M2/M3)

Если приложение экстренно завершает работу на Apple Silicon:

1. **Запустите диагностику:**
   ```bash
   python3 check_architecture.py
   ```

2. **Переустановите MySQL connector для ARM64:**
   ```bash
   pip3 install --force-reinstall --no-cache-dir mysql-connector-python
   ```

3. **Пересоберите приложение:**
   ```bash
   rm -rf build dist CarSelection.app
   ./build_macos_app_py2app.sh
   ```

4. **Проверьте архитектуру собранного приложения:**
   ```bash
   file CarSelection.app/Contents/MacOS/CarSelection
   ```
   Должно содержать `arm64`

---

## Подробная инструкция

## Предварительные требования

1. **macOS** (любая версия с поддержкой Python 3.7+)
   - Поддерживаются процессоры Intel (x86_64) и Apple Silicon (M1/M2/M3, arm64)
2. **Python 3.7 или выше**
   - ⚠️ **Важно для Apple Silicon:** Используйте нативный Python для ARM64, а не через Rosetta 2
   - Проверьте: `python3 -c "import platform; print(platform.machine())"` - должно быть `arm64`
3. **MySQL Server** (должен быть установлен на целевом компьютере)
4. **py2app** (устанавливается автоматически скриптом)

## Установка зависимостей

```bash
pip install -r requirements.txt
pip install py2app
```

## Сборка приложения

### Способ 1: Использование скрипта (рекомендуется)

1. Сделайте скрипт исполняемым:
```bash
chmod +x build_macos_app_py2app.sh
```

2. Запустите скрипт:
```bash
./build_macos_app_py2app.sh
```

### Способ 2: Ручная сборка

```bash
python3 setup.py py2app
```

После сборки приложение будет находиться в папке `dist/CarSelection.app`

## Результат сборки

После успешной сборки вы получите:
- **CarSelection.app** — приложение macOS, готовое к использованию

## Запуск приложения

### Двойной клик
Просто дважды кликните на `CarSelection.app` в Finder

### Из терминала
```bash
open CarSelection.app
```

## Распространение приложения

### Важные замечания

⚠️ **MySQL Server должен быть установлен на целевом компьютере!**

Приложение использует MySQL для хранения данных, поэтому на каждом компьютере, где будет запускаться приложение, должен быть установлен и настроен MySQL Server.

### Создание архива для распространения

```bash
zip -r CarSelection.zip CarSelection.app
```

### Создание DMG образа (опционально)

Для создания DMG образа можно использовать:
- **create-dmg** (npm пакет)
- **DMG Canvas** (платное приложение)
- Вручную через Disk Utility

## Настройка на целевом компьютере

После установки приложения на другой Mac:

1. **Установите MySQL Server** (если еще не установлен):
```bash
brew install mysql
brew services start mysql
```

2. **Настройте подключение к MySQL:**
   - Откройте `CarSelection.app/Contents/MacOS/config.py` (если файл там)
   - Или создайте `config.py` рядом с приложением
   - Укажите параметры подключения к MySQL

3. **Запустите приложение**

## Решение проблем

### Диагностика проблем с Apple Silicon (M1/M2/M3)

Если приложение экстренно завершает работу на Apple Silicon, запустите диагностический скрипт:

```bash
python3 check_architecture.py
```

Этот скрипт проверит:
- Архитектуру процессора и Python
- Установленные зависимости
- Совместимость MySQL connector
- Архитектуру собранного приложения
- Права доступа

### Приложение экстренно завершает работу на Apple Silicon

**Проблема:** Приложение собранное на/для Apple Silicon может завершаться с ошибкой из-за несовместимости архитектур.

**Решение:**

1. **Проверьте архитектуру Python:**
   ```bash
   python3 -c "import platform; print(platform.machine())"
   ```
   Должно быть `arm64` для Apple Silicon

2. **Переустановите MySQL connector для правильной архитектуры:**
   ```bash
   pip3 uninstall mysql-connector-python
   pip3 install --force-reinstall --no-cache-dir mysql-connector-python
   ```

3. **Пересоберите приложение:**
   ```bash
   rm -rf build dist CarSelection.app
   ./build_macos_app_py2app.sh
   ```

4. **Проверьте архитектуру собранного приложения:**
   ```bash
   file CarSelection.app/Contents/MacOS/CarSelection
   ```
   Должно содержать `arm64`

5. **Запустите из терминала для просмотра ошибок:**
   ```bash
   ./CarSelection.app/Contents/MacOS/CarSelection
   ```

### Ошибка: "MySQL server not found"

**Решение:** Установите MySQL Server на Mac:
```bash
brew install mysql
brew services start mysql
```

### Ошибка: "Permission denied"

**Решение:** Дайте права на выполнение:
```bash
chmod +x CarSelection.app/Contents/MacOS/CarSelection
```

### Ошибка: "Launch Error: See the py2app website for debugging launch issues"

**Проблема:** Обычно связана с ошибкой `SyntaxError: source code string cannot contain null bytes` в tkinter.

**Решение:** См. подробную инструкцию в файле `fix_launch_error.md`

**Быстрое решение:**
```bash
# Пересоберите приложение с текущими настройками
rm -rf build dist CarSelection.app
./build_macos_app_py2app.sh
```

### Приложение не запускается

**Решение:**
1. Проверьте логи в Console.app
2. Попробуйте запустить из терминала:
```bash
./CarSelection.app/Contents/MacOS/CarSelection
```

3. Если возникают проблемы с зависимостями, попробуйте пересобрать:
```bash
python3 setup.py py2app -A
```
Флаг `-A` создает псевдо-приложение с символическими ссылками (для отладки).

4. **Для Apple Silicon:** Убедитесь, что используете нативный Python для ARM64, а не через Rosetta 2.

5. **Для Python 3.13+:** Текущий setup.py использует `semi_standalone: True` для избежания проблем с упаковкой стандартной библиотеки.

### Gatekeeper блокирует запуск

**Решение:** Разрешите запуск в System Preferences → Security & Privacy:
```bash
xattr -cr CarSelection.app
```

## Альтернативные способы сборки

Если py2app не работает с Python 3.13+, доступны несколько альтернатив:

### 1. Briefcase (BeeWare) ⭐ РЕКОМЕНДУЕТСЯ

Лучший выбор для Python 3.13+ и Apple Silicon:

```bash
pip3 install briefcase
./build_briefcase.sh
```

Подробнее: см. `BRIEFCASE_INSTRUCTIONS.md`

### 2. Nuitka

Компилятор Python в нативный код - лучшая производительность:

```bash
pip3 install nuitka
./build_nuitka.sh
```

### 3. cx_Freeze

Простая альтернатива с хорошей поддержкой:

```bash
pip3 install cx_Freeze
./build_cxfreeze.sh
```

### 4. PyInstaller (старый метод)

```bash
pip install pyinstaller
./build_macos_app.sh
```

**Примечание:** PyInstaller может работать некорректно с Python 3.13+. Для Python 3.13+ рекомендуется использовать Briefcase.

**Сравнение всех альтернатив:** см. `ALTERNATIVES.md` и `QUICK_START_ALTERNATIVES.md`

## Дополнительные настройки

### Добавление иконки

1. Создайте файл `icon.icns`
2. Откройте `setup.py` и измените строку `'iconfile': None,` на `'iconfile': 'icon.icns',`

### Подпись приложения (для распространения)

Для подписи приложения (опционально):
```bash
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" CarSelection.app
```

---

**Примечание:** Приложение требует MySQL Server на целевом компьютере. Для полностью автономного приложения рассмотрите возможность использования SQLite вместо MySQL.


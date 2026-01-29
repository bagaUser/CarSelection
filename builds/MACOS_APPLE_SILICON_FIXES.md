# Исправления для сборки на Mac OS Apple Silicon

## Выявленные проблемы и исправления

### 1. Отсутствие setup.py для py2app
**Проблема:** Скрипт `build_macos_app_py2app.sh` ссылался на `setup.py`, который отсутствовал.

**Исправление:** 
- Создан файл `setup.py` с правильной конфигурацией для py2app
- Настроена поддержка как Intel (x86_64), так и Apple Silicon (arm64)
- Для Python 3.13+ на Apple Silicon используется `alias` режим вместо `semi_standalone`

### 2. Неправильные hidden-import для PyInstaller (build_macos_app.sh)
**Проблема:** Скрипт использовал `--hidden-import=tkinter`, но приложение использует PyQt6, не tkinter.

**Исправление:**
- Заменен `--hidden-import=tkinter` на правильные импорты PyQt6:
  - `--hidden-import=PyQt6`
  - `--hidden-import=PyQt6.QtCore`
  - `--hidden-import=PyQt6.QtGui`
  - `--hidden-import=PyQt6.QtWidgets`
- Добавлены импорты для модулей приложения:
  - `--hidden-import=database`
  - `--hidden-import=expert_system`
- Добавлены коллекторы:
  - `--collect-all=mysql.connector`
  - `--collect-submodules=PyQt6`

### 3. Отсутствие проверки архитектуры в build_macos_app.sh
**Проблема:** Скрипт не определял архитектуру процессора для правильной сборки.

**Исправление:**
- Добавлено определение архитектуры через `uname -m`
- Добавлены сообщения о том, какая архитектура обнаружена
- Это помогает понять, для какой платформы происходит сборка

### 4. Неполная проверка зависимостей для Apple Silicon
**Проблема:** В скрипте `build_macos_app_py2app.sh` не было проверки PyQt6 для Apple Silicon.

**Исправление:**
- Добавлена проверка наличия setup.py перед сборкой
- Добавлена проверка PyQt6 для Apple Silicon с предупреждением, если библиотека установлена неправильно
- Добавлены инструкции по переустановке зависимостей для ARM64

## Конфигурация setup.py для Apple Silicon

### Настройки для разных архитектур:

1. **Apple Silicon (arm64) с Python 3.13+:**
   - Используется `alias: True`
   - `semi_standalone: False`
   - Это необходимо для избежания проблем с упаковкой стандартной библиотеки

2. **Intel (x86_64) с Python 3.13+:**
   - Используется `semi_standalone: True`
   - `alias: False`

3. **Python < 3.13 (любая архитектура):**
   - Стандартный режим py2app
   - `semi_standalone: False`
   - `alias: False`

### Включенные модули:

```python
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
```

## Рекомендации для сборки на Apple Silicon

### 1. Использование правильного Python

Убедитесь, что используете нативный Python для ARM64, а не через Rosetta 2:

```bash
# Проверка архитектуры Python
python3 -c "import platform; print(platform.machine())"
# Должно вывести: arm64

# Если выводит x86_64, вы используете Rosetta 2 - установите нативный Python для ARM64
```

### 2. Переустановка зависимостей для ARM64

Перед сборкой убедитесь, что все зависимости установлены для правильной архитектуры:

```bash
# Переустановка PyQt6 для ARM64
pip3 install --force-reinstall --no-cache-dir PyQt6

# Переустановка mysql-connector-python для ARM64
pip3 install --force-reinstall --no-cache-dir mysql-connector-python
```

### 3. Проверка перед сборкой

Запустите скрипт проверки архитектуры:

```bash
# Проверка архитектуры системы
uname -m  # Должно вывести: arm64

# Проверка архитектуры Python
python3 -c "import platform; print(platform.machine())"  # Должно вывести: arm64

# Проверка архитектуры библиотек
python3 -c "import PyQt6; import platform; print('PyQt6 OK, arch:', platform.machine())"
```

## Известные проблемы и решения

### Проблема: Приложение не запускается на Apple Silicon

**Возможные причины:**
1. Приложение собрано для Intel, а запускается на Apple Silicon
2. Библиотеки установлены для неправильной архитектуры
3. Проблемы с code signing

**Решения:**

1. **Проверьте архитектуру приложения:**
```bash
file CarSelection.app/Contents/MacOS/CarSelection
# Должно содержать: arm64 (для Apple Silicon)
```

2. **Переустановите зависимости:**
```bash
pip3 install --force-reinstall --no-cache-dir PyQt6 mysql-connector-python
```

3. **Удалите атрибуты quarantine:**
```bash
xattr -cr CarSelection.app
```

### Проблема: Ошибки при сборке с Python 3.13+

**Решение:** 
Текущий `setup.py` автоматически определяет версию Python и использует правильный режим:
- Для Apple Silicon: `alias` режим
- Для Intel: `semi_standalone` режим

### Проблема: MySQL connector не работает

**Решение:**
Убедитесь, что `mysql-connector-python` установлен для правильной архитектуры:

```bash
pip3 uninstall mysql-connector-python
pip3 install --no-cache-dir mysql-connector-python
```

## Использование исправленных скриптов

### Для сборки с py2app (рекомендуется):

```bash
chmod +x builds/build_macos_app_py2app.sh
./builds/build_macos_app_py2app.sh
```

Скрипт автоматически:
- Проверит архитектуру процессора
- Проверит наличие setup.py
- Проверит зависимости для правильной архитектуры
- Запустит сборку с правильными настройками

### Для сборки с PyInstaller:

```bash
chmod +x builds/build_macos_app.sh
./builds/build_macos_app.sh
```

Скрипт автоматически:
- Проверит архитектуру процессора
- Использует правильные hidden-import для PyQt6
- Создаст .app bundle для обнаруженной архитектуры

## Проверка результата сборки

После сборки проверьте:

1. **Архитектуру приложения:**
```bash
file dist/CarSelection.app/Contents/MacOS/CarSelection
```

2. **Запуск из терминала (для отладки):**
```bash
./CarSelection.app/Contents/MacOS/CarSelection
```

3. **Логи (если есть проблемы):**
```bash
# В консоли macOS или через Console.app
log show --predicate 'process == "CarSelection"' --last 5m
```

## Заключение

Все проблемы для сборки на Mac OS Apple Silicon были исправлены:

✅ Создан `setup.py` с поддержкой Apple Silicon  
✅ Исправлены hidden-import в скриптах PyInstaller  
✅ Добавлены проверки архитектуры  
✅ Добавлены проверки зависимостей для ARM64  
✅ Настроен правильный режим для Python 3.13+ на Apple Silicon  

Приложение теперь должно успешно собираться и запускаться на Mac OS Apple Silicon.


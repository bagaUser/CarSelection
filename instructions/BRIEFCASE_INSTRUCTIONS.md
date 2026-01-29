# Инструкция по использованию Briefcase

## Установка

```bash
pip3 install briefcase
```

## Быстрый старт

### Вариант 1: Использование существующего pyproject.toml

1. Убедитесь, что файл `pyproject.toml` содержит правильную конфигурацию (он уже создан)

2. Запустите сборку:
   ```bash
   ./build_briefcase.sh
   ```

### Вариант 2: Инициализация нового проекта

1. Инициализируйте проект Briefcase:
   ```bash
   briefcase new
   ```
   
   Ответьте на вопросы:
   - Formal Name: `CarSelection`
   - App Name: `carselection`
   - Bundle: `com.carselection`
   - Project Name: `CarSelection`

2. Обновите зависимости:
   ```bash
   briefcase update
   ```

3. Соберите приложение:
   ```bash
   briefcase build macOS
   ```

4. Запустите приложение:
   ```bash
   briefcase run macOS
   ```

5. Создайте DMG для распространения:
   ```bash
   briefcase package macOS
   ```

## Структура проекта после инициализации

```
Project-1/
├── pyproject.toml          # Конфигурация Briefcase
├── src/
│   └── carselection/       # Исходный код (будет создан)
│       ├── app.py          # Главный файл
│       └── __init__.py
├── macOS/                  # Файлы для macOS (создастся автоматически)
└── ...
```

## Настройка pyproject.toml

Если вы используете существующие файлы (main.py, database.py и т.д.), нужно:

1. Скопировать файлы в структуру Briefcase, или
2. Обновить `sources` в pyproject.toml для указания правильных путей

Пример обновленного pyproject.toml:

```toml
[tool.briefcase.app.carselection]
sources = [
    "../main.py",
    "../database.py",
    "../expert_system.py",
    "../config.py",
]
```

## Преимущества Briefcase

- ✅ Отличная поддержка Python 3.13+
- ✅ Нативная поддержка Apple Silicon
- ✅ Создает правильные .app bundles
- ✅ Автоматическая обработка зависимостей
- ✅ Возможность создания DMG

## Устранение проблем

Если возникают ошибки:

1. Проверьте версию Python:
   ```bash
   python3 --version
   ```
   Должна быть 3.10+ (3.13+ рекомендуется)

2. Обновите Briefcase:
   ```bash
   pip3 install --upgrade briefcase
   ```

3. Пересоздайте проект:
   ```bash
   briefcase dev
   ```

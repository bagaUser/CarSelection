# Установка и настройка MySQL

## Установка MySQL

### Windows

1. Скачайте MySQL Installer с официального сайта: https://dev.mysql.com/downloads/installer/
2. Запустите установщик и выберите "Developer Default" или "Server only"
3. В процессе установки:
   - Выберите "Standalone MySQL Server"
   - Установите пароль для пользователя root (запомните его!)
   - Оставьте порт по умолчанию: 3306

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

### macOS

```bash
brew install mysql
brew services start mysql
```

## Установка Python библиотеки

После установки MySQL установите драйвер для Python:

```bash
pip install mysql-connector-python
```

Или используйте requirements.txt:

```bash
pip install -r requirements.txt
```

## Настройка приложения

### Способ 1: Использование config.py (рекомендуется)

1. Откройте файл `config.py`
2. Измените параметры подключения:

```python
MYSQL_CONFIG = {
    'host': 'localhost',           # Адрес MySQL сервера
    'user': 'root',                # Ваше имя пользователя MySQL
    'password': 'ваш_пароль',      # Ваш пароль MySQL
    'database': 'Auto_Selection'    # Имя базы данных
}
```

### Способ 2: Изменение в main.py

Если файл `config.py` не используется, измените параметры в `main.py` напрямую:

```python
self.db = Database(
    host='localhost',
    user='root',
    password='ваш_пароль',  # Измените на свой пароль
    database='Auto_Selection'
)
```

## Проверка подключения

### Проверка через командную строку MySQL

```bash
mysql -u root -p
```

Введите пароль. Если подключение успешно, вы увидите приглашение `mysql>`.

### Проверка через Python

Запустите тестовый скрипт:

```bash
python test_system.py
```

Если все настроено правильно, вы увидите сообщение об успешной инициализации базы данных.

## Создание базы данных

**Примечание:** База данных создается автоматически при первом запуске приложения, если её не существует.

Если вы хотите создать базу данных вручную:

```sql
CREATE DATABASE IF NOT EXISTS AutoSelection;
```

## Права пользователя

Убедитесь, что у указанного пользователя есть права на:
- Создание баз данных
- Создание таблиц
- Вставку данных
- Выборку данных

Если возникают проблемы с правами, выполните в MySQL:

```sql
GRANT ALL PRIVILEGES ON AutoSelection.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

## Решение проблем

### Ошибка: "Access denied for user"

- Проверьте правильность имени пользователя и пароля
- Убедитесь, что пользователь существует в MySQL
- Проверьте права доступа пользователя

### Ошибка: "Can't connect to MySQL server"

- Убедитесь, что MySQL сервер запущен
- Проверьте, что хост и порт указаны правильно
- Проверьте файрволл (MySQL использует порт 3306)

### Ошибка: "Unknown database"

- База данных должна создаваться автоматически
- Проверьте права пользователя на создание баз данных
- Создайте базу данных вручную (см. выше)

### Запуск MySQL сервера

**Windows:**
```bash
# Через службы Windows
services.msc -> MySQL -> Запустить

# Или через командную строку (если установлен как служба)
net start MySQL
```

**Linux:**
```bash
sudo systemctl start mysql
# или
sudo service mysql start
```

**macOS:**
```bash
brew services start mysql
```

## Важные замечания

1. **Безопасность паролей**: Не коммитьте файл `config.py` с реальными паролями в публичные репозитории. Используйте `.gitignore`.

2. **Для продакшн окружения**: Используйте отдельного пользователя MySQL с ограниченными правами, а не root.

3. **Резервное копирование**: Регулярно делайте резервные копии базы данных:
   ```bash
   mysqldump -u root -p AutoSelection > backup.sql
   ```

4. **Для сборки в exe**: При сборке в исполняемый файл MySQL должен быть установлен на целевом компьютере, и пользователь должен настроить подключение вручную или через конфигурационный файл.


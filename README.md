# TeleBotCore

# TeleBotCore - Modular Telegram Bot Template

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Aiogram](https://img.shields.io/badge/Aiogram-3.22-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Модульный шаблон для создания Telegram ботов с системой плагинов**

[Особенности](#Особенности) • [Быстрый старт](#быстрый-старт) • [Архитектура](#архитектура) • [Документация](#документация) • [Лицензия](#лицензия) • [Авторы](#авторы)

</div>

## Особенности

### **Модульная архитектура**
- **Система плагинов** - динамическая загрузка и управление
- **Авторегистрация** - плагины автоматически обнаруживаются и регистрируются
- **Изоляция** - каждый плагин работает в своем пространстве

### **Готовые компоненты**
- **База данных** - Async SQLAlchemy с моделями и миграциями
- **Аутентификация** - система ролей и прав доступа
- **FSM** - конечные автоматы для сложных сценариев
- **Клавиатуры** - гибкая система построения интерфейсов
- **Конфигурация** - Pydantic settings с env файлами

### **Профессиональная архитектура**
- **Dependency Injection** - чистая инжекция зависимостей
- **Middleware** - пользовательские и плагинные middleware
- **Обработка ошибок** - глобальный error handling
- **Логирование** - структурированные логи с контекстом

## Быстрый старт

### 1. Установка
```bash
git clone https://github.com/yourname/TeleBotCore.git
cd TeleBotCore

# Базовая установка
pip install .

# С SQLite (по умолчанию)
pip install ".[sqlite]"

# С PostgreSQL  
pip install ".[postgres]"

# Для разработки
pip install ".[dev]"

# Всё сразу
pip install ".[sqlite,dev]"
````

### 2. Настройка
```.dotenv
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=[123456789]
DATABASE_URL=sqlite+aiosqlite:///db.sqlite3
SUPPORT=your_support_username
PLUGINS_DISPLAY_MODE=integrated
```

### 3. Запуск
```bash
python main.py
```

### Разработка
```bash
git clone https://github.com/gambojo/TeleBotCore.git
cd TeleBotCore
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Архитектура
### Структура проекта
```
TeleBotCore/
├── ЯДРО СИСТЕМЫ (core/)
├── БАЗА ДАННЫХ (databases/) 
├── ПЛАГИНЫ (plugins/)
├── ТОЧКА ВХОДА (main.py)
└── КОНФИГУРАЦИЯ (config files)
```

### CORE/ - Ядро системы
#### Конфигурация (config/)
````
core/config/
├── manager.py       # ConfigManager - единая точка управления настройками
├── base_config.py   # CoreSettings - базовые настройки (Pydantic)
└── __init__.py      # Экспорт компонентов
````

#### Аутентификация (auth/)
```
core/auth/
├── auth.py          # AuthManager - система ролей и прав доступа
└── __init__.py
```

#### Пользовательский интерфейс (display/)
```
core/display/
├── html_builder.py     # HTMLBuilder - безопасное форматирование текста
├── image_manager.py    # ImageManager - управление изображениями/баннерами
└── images/             # Ресурсы изображений
```

#### Клавиатуры (keyboards/)
```
core/keyboards/
├── keyboard_builder_base.py  # Базовый построитель клавиатур
├── main_menu_keyboard.py     # MainMenuKeyboard - главное меню
└── __init__.py
```

#### Безопасность и фильтры (filters/)
```
core/filters/
├── base.py           # Базовые фильтры: RoleFilter, PermissionFilter, GroupFilter
└── __init__.py
```

#### Промежуточное ПО (middlewares/)
```
core/middlewares/
├── user_init.py        # UserInitMiddleware - инициализация пользователей
├── plugin_logger.py    # PluginLoggerMiddleware - логирование плагинов
└── __init__.py
```

#### Состояния (fsm/)
```
core/fsm/
├── registry.py           # StatesGroup: ConfirmFSM, UserFSM, AdminFSM, PluginFSM
├── filter_configurator.py # FilterConfigurator - настройка фильтров через FSM
└── __init__.py
```

#### Обработчики (handlers/)
```
core/handlers/
├── start.py        # StartHandler - команда /start и главное меню
├── errors.py       # ErrorHandler - глобальная обработка ошибок  
├── fallback.py     # FallbackHandler - необработанные callback'ы
└── __init__.py
```

#### Логирование (logging/)
```
core/logging/
├── logging.py      # LoggingManager + PluginLoggerAdapter
└── __init__.py
```

#### Система плагинов (plugins/)
```
core/plugins/
├── registry.py         # PluginRegistry - реестр плагинов
├── global_registry.py  # Глобальный экземпляр реестра
├── manager.py          # PluginManager - загрузка и управление плагинами
├── base.py             # PluginBase - абстрактный базовый класс плагина
└── __init__.py
```

### DATABASES/ - Работа с данными
#### Модели и менеджеры
```
databases/
├── models.py           # Базовые модели: User, UserMetrics
├── user_manager.py     # UserManager - CRUD операции с пользователями
├── database_manager.py # DatabaseManager - управление подключениями к БД
├── exceptions.py       # Кастомные исключения БД
└── __init__.py
```

### PLUGINS/ - Модульная система
#### Базовая структура плагина
```
plugins/{plugin_name}/
├── plugin.py           # Основной класс (наследует от PluginBase)
├── config.py           # Настройки плагина (Pydantic)
├── handlers.py         # Обработчики команд и callback'ов
├── keyboards.py        # Клавиатуры плагина
├── fsm.py              # Состояния FSM плагина
├── models.py           # Модели данных (опционально)
├── services/           # Бизнес-логика
│   ├── service.py      # Базовый сервис
│   └── *.py            # Модули сервиса
├── __init__.py         # Регистрация плагина
└── ...
```

### Разработка плагинов
* [Шаблон плагина - TeleBotPlugin](https://github.com/gambojo/TeleBotPlugin.git)
* [Документация](https://github.com/gambojo/TeleBotPlugin.git#readme)


## Лицензия
Этот проект распространяется под лицензией MIT.

## Авторы
* Агамов Гамид • [GitHub](https://github.com/gambojo) • [Telegram](https://t.me/gambo_jo)

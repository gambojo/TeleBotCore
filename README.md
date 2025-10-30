# TeleBotCore

# TeleBotCore - Modular Telegram Bot Template

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Aiogram](https://img.shields.io/badge/Aiogram-3.22-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Модульный шаблон для создания Telegram ботов с системой плагинов**

[Особенности](#Особенности) • [Быстрый старт](#быстрый-старт) • [Архитектура](#архитектура) • [Документация](#документация)

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
pip install -r requirements.txt
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

## Архитектура
```
TeleBotCore/
├── core/                   # Ядро системы
│   ├── bot/                # Основной класс бота
│   ├── config/             # Менеджер конфигурации
│   ├── plugins/            # Система плагинов
│   ├── filters/            # Фильтры для хендлеров
│   ├── middlewares/        # Промежуточное ПО
│   ├── keyboards/          # Построители клавиатур
│   ├── display/            # HTML и изображения
│   └── handlers/           # Базовые обработчики
├── databases/              # Работа с БД
│   ├── models.py           # Базовые модели
│   ├── user_manager.py     # Управление пользователями
│   └── database_manager.py # Управление сессией
├── plugins/                # Плагины
│   └── __init__.py         # Автоимпорт плагиноа
└── main.py                 # Точка входа
```

## Создание плагина
### 1. Структура плагина
```
plugins/
└── my_plugin/
    ├── __init__.py     # Регистрация плагина
    ├── config.py       # Настройки плагина
    ├── plugin.py       # Основной класс плагина
    ├── handlers.py     # Обработчики
    ├── keyboards.py    # Клавиатуры
    ├── models.py       # Модели БД (опционально)
    ├── services.py     # Бизнес-логика
    └── fsm.py          # Состояния (опционально)
```

### 2. Пример плагина
`plugins/my_plugin/config.py`
```python
from pydantic_settings import BaseSettings

# Включить/выключить плагин
ENABLED: bool = True

class PluginSettings(BaseSettings):
    API_KEY: str = "default_key"
    MAX_USERS: int = 100
    
    model_config = {"env_file": ".env", "env_prefix": "MYPLUGIN_"}
```

`plugins/my_plugin/plugin.py`
```python
from core.plugins.base import PluginBase
from core.config import ConfigManager
from aiogram import Router
from aiogram.types import InlineKeyboardButton
from databases import DatabaseManager
from .config import PluginSettings
from .handlers import PluginHandlers

class Plugin(PluginBase):
    def __init__(self, config: ConfigManager, db: DatabaseManager):
        self.config = config
        self.db = db
        self.settings = config.load_plugin_config(self.get_name(), PluginSettings)

    def get_router(self) -> Router:
        router = Router(name=self.get_name())
        PluginHandlers(self.settings, self.get_name(), self.db).register(router)
        return router

    def get_integrated_buttons(self):
        return [[InlineKeyboardButton(text="Мой плагин", callback_data="myplugin:main")]]

    def get_entry_button(self):
        return [[InlineKeyboardButton(text="📱 Мой плагин", callback_data="plugin:MYPLUGIN")]]

    def get_config(self):
        return PluginSettings

    def get_settings(self):
        return self.settings
```

`plugins/my_plugin/__init__.py`
```python
from .plugin import Plugin
from core.plugins.registry import register_plugin

register_plugin("my_plugin", lambda config, db: Plugin(config, db))
```

## Конфигурация
### Основные настройки (.env)
```dotenv
# Обязательные
BOT_TOKEN=your_bot_token
ADMIN_IDS=[123456,789012]

# Опциональные
DATABASE_URL=sqlite+aiosqlite:///db.sqlite3
SUPPORT=username_support_bot
PLUGINS_DISPLAY_MODE=integrated  # integrated|entry|smart
```

## Режимы отображения плагинов
* `integrated` - кнопки плагинов в главном меню
* `entry` - одна кнопка входа в каждый плагин
* `smart` - автоматический выбор на основе количества кнопок

## API разработчика
### Фильтры доступа
```python
from core.filters import RoleFilter, PermissionFilter

@router.message(RoleFilter(user_manager, "admin"))
async def admin_command(message: Message):
    await message.answer("Админ команда")

@router.message(PermissionFilter(user_manager, is_admin=True))
async def moderator_command(message: Message):
    await message.answer("Модератор команда")
```

### Работа с БД
```python
from databases import UserManager

user_manager = UserManager()
user, created = await user_manager.ensure(
    telegram_id=message.from_user.id,
    username=message.from_user.username
)
```

### FSM состояния
```python
from aiogram.fsm.context import FSMContext
from core.fsm.registry import UserFSM

@router.message(UserFSM.awaiting_email)
async def handle_email(message: Message, state: FSMContext):
    email = message.text
    await state.update_data(email=email)
    await message.answer("Email сохранен!")
```

## Разработка
```bash
git clone https://github.com/gambojo/TeleBotCore.git
cd TeleBotCore
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Создание нового плагина
...

## Лицензия
Этот проект распространяется под лицензией MIT.

## Авторы
* Агамов Гамид - https://github.com/gambojo

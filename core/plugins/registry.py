from typing import Callable
from core.config import ConfigManager
from databases import DatabaseManager
from core.plugins.base import PluginBase

_plugins: dict[str, Callable[[ConfigManager, DatabaseManager], PluginBase]] = {}

def register_plugin(directory_name: str, factory: Callable[[ConfigManager, DatabaseManager], PluginBase]):
    """
    Регистрирует фабрику плагина по имени директории
    Параметры: directory_name - имя папки плагина, factory - фабричная функция
    Возвращает: None
    Пример: register_plugin('vpn', lambda config, db: VPNManager(config, db))
    """
    _plugins[directory_name] = factory

def get_registered_plugins() -> dict[str, Callable[[ConfigManager, DatabaseManager], PluginBase]]:
    """
    Возвращает все зарегистрированные фабрики плагинов
    Возвращает: dict - словарь фабрик плагинов
    Пример: factories = get_registered_plugins()
    """
    return _plugins

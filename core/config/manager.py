from typing import Type, TypeVar
from pydantic_settings import BaseSettings
from .base_config import CoreSettings

T = TypeVar('T', bound=BaseSettings)


class ConfigManager:
    """
    Менеджер конфигурации для загрузки настроек ядра и плагинов
    Параметры: не принимает параметров при создании
    Возвращает: экземпляр ConfigManager
    Пример: config = ConfigManager()
    """

    def __init__(self):
        self.settings = CoreSettings()
        self.plugin_configs: dict[str, BaseSettings] = {}
        self.plugin_manager = None

    def set_plugin_manager(self, plugin_manager):
        """Устанавливает PluginManager для доступа плагинами"""
        self.plugin_manager = plugin_manager

    def get_plugin_manager(self):
        """Возвращает PluginManager"""
        return self.plugin_manager

    def load_plugin_config(self, name: str, config_class: Type[T]) -> T:
        """
        Загружает конфигурацию для плагина
        Параметры: name - имя плагина, config_class - класс конфигурации
        Возвращает: экземпляр конфигурации плагина
        Пример: vpn_config = config.load_plugin_config('VPN', VPNConfig)
        """
        plugin_config = config_class()
        self.plugin_configs[name] = plugin_config
        return plugin_config

    def get_plugin_config(self, name: str) -> BaseSettings:
        """
        Получает загруженную конфигурацию плагина
        Параметры: name - имя плагина
        Возвращает: BaseSettings - конфигурация плагина
        Пример: config.get_plugin_config('VPN')
        """
        return self.plugin_configs[name]

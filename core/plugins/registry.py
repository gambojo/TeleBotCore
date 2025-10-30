from typing import Callable, Dict
from core.config import ConfigManager
from databases import DatabaseManager
from core.plugins.base import PluginBase
from core.logging import LoggingManager


class PluginRegistry:
    """
    Реестр для управления регистрацией и хранением плагинов
    Параметры: не принимает параметров при создании
    Возвращает: экземпляр PluginRegistry
    Пример: registry = PluginRegistry()
    """

    def __init__(self):
        self._plugins: Dict[str, Callable[[ConfigManager, DatabaseManager], PluginBase]] = {}
        self.logger = LoggingManager().get_logger(__name__)

    def register(self, directory_name: str, factory: Callable[[ConfigManager, DatabaseManager], PluginBase]) -> None:
        """
        Регистрирует фабрику плагина по имени директории
        Параметры: directory_name - имя папки плагина, factory - фабричная функция
        Возвращает: None
        Пример: registry.register('vpn', lambda config, db: VPNManager(config, db))
        """
        if directory_name in self._plugins:
            self.logger.warning(f"Plugin '{directory_name}' is already registered, overwriting")

        self._plugins[directory_name] = factory
        self.logger.info(f"Plugin '{directory_name}' registered successfully")

    def get_all(self) -> Dict[str, Callable[[ConfigManager, DatabaseManager], PluginBase]]:
        """
        Возвращает все зарегистрированные фабрики плагинов
        Возвращает: dict - словарь фабрик плагинов
        Пример: factories = registry.get_all()
        """
        return self._plugins.copy()

    def get_factory(self, directory_name: str) -> Callable[[ConfigManager, DatabaseManager], PluginBase]:
        """
        Возвращает фабрику плагина по имени директории
        Параметры: directory_name - имя папки плагина
        Возвращает: Callable - фабричная функция
        Пример: factory = registry.get_factory('vpn')
        """
        if directory_name not in self._plugins:
            raise KeyError(f"Plugin '{directory_name}' is not registered")
        return self._plugins[directory_name]

    def is_registered(self, directory_name: str) -> bool:
        """
        Проверяет зарегистрирован ли плагин
        Параметры: directory_name - имя папки плагина
        Возвращает: bool - True если плагин зарегистрирован
        Пример: registry.is_registered('vpn') -> True
        """
        return directory_name in self._plugins

    def unregister(self, directory_name: str) -> bool:
        """
        Удаляет плагин из реестра
        Параметры: directory_name - имя папки плагина
        Возвращает: bool - True если плагин был удален
        Пример: registry.unregister('vpn') -> True
        """
        if directory_name in self._plugins:
            del self._plugins[directory_name]
            self.logger.info(f"Plugin '{directory_name}' unregistered")
            return True
        return False

    def clear(self) -> None:
        """
        Очищает весь реестр плагинов
        Возвращает: None
        Пример: registry.clear()
        """
        plugin_count = len(self._plugins)
        self._plugins.clear()
        self.logger.info(f"Registry cleared, removed {plugin_count} plugins")

    def get_names(self) -> list[str]:
        """
        Возвращает список имен зарегистрированных плагинов
        Возвращает: list[str] - список имен плагинов
        Пример: names = registry.get_names() -> ['vpn', 'template']
        """
        return list(self._plugins.keys())

    def count(self) -> int:
        """
        Возвращает количество зарегистрированных плагинов
        Возвращает: int - количество плагинов
        Пример: registry.count() -> 2
        """
        return len(self._plugins)


# Глобальный экземпляр для обратной совместимости
_global_registry = PluginRegistry()

# Функции для обратной совместимости
def register_plugin(directory_name: str, factory: Callable[[ConfigManager, DatabaseManager], PluginBase]):
    _global_registry.register_plugin(directory_name, factory)

def get_registered_plugins() -> Dict[str, Callable[[ConfigManager, DatabaseManager], PluginBase]]:
    return _global_registry.get_registered_plugins()

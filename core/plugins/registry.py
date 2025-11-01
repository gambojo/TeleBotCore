from typing import Callable, Dict
from core.config import ConfigManager
from modules.databases import DatabaseManager
from core.plugins.base import PluginBase
from core.logging import LoggingManager
import inspect
import os


class PluginRegistry:
    """
    Реестр для управления регистрацией и хранением плагинов (синглтон)
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._plugins: Dict[str, Callable[[ConfigManager, DatabaseManager], PluginBase]] = {}
            self.logger = LoggingManager().get_logger(__name__)
            self._initialized = True

    def register(self, factory: Callable[[ConfigManager, DatabaseManager], PluginBase]) -> None:
        """
        Регистрирует фабрику плагина (автоматически определяет имя из директории)
        Параметры: factory - фабричная функция
        Возвращает: None
        Пример: registry.register(lambda config, db: Plugin(config, db))
        """
        # Автоматически определяем имя плагина из директории фабричной функции
        plugin_dir_name = self._get_plugin_directory_name(factory)

        if plugin_dir_name in self._plugins:
            self.logger.warning(f"Plugin '{plugin_dir_name}' is already registered, overwriting")

        self._plugins[plugin_dir_name] = factory
        self.logger.info(f"Plugin '{plugin_dir_name}' registered successfully")

    def _get_plugin_directory_name(self, factory: Callable) -> str:
        """Автоматически определяет имя директории плагина из фабричной функции"""
        try:
            # Получаем файл, где определена фабричная функция
            factory_file = inspect.getfile(factory)

            # Ищем папку plugins в пути и берем следующую папку
            path_parts = os.path.normpath(factory_file).split(os.sep)

            if 'plugins' in path_parts:
                plugins_index = path_parts.index('plugins')
                if plugins_index + 1 < len(path_parts):
                    return path_parts[plugins_index + 1]

            # Если не нашли, используем имя модуля как fallback
            return factory.__module__.split('.')[1] if '.' in factory.__module__ else 'unknown'

        except (TypeError, IndexError) as e:
            self.logger.warning(f"Could not determine plugin directory name: {e}")
            return 'unknown'

    def register_with_name(self, directory_name: str,
                           factory: Callable[[ConfigManager, DatabaseManager], PluginBase]) -> None:
        """
        Регистрирует фабрику плагина с явным указанием имени (для обратной совместимости)
        Параметры: directory_name - имя папки плагина, factory - фабричная функция
        Возвращает: None
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

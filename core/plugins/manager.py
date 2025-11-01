from aiogram import Dispatcher, Router
from typing import Dict, List, Optional
from core.plugins.base import PluginBase
from core.config import ConfigManager
from modules.databases import DatabaseManager
from .registry import PluginRegistry
from core.logging import LoggingManager
import importlib


class PluginManager:
    def __init__(self, config_manager: ConfigManager, db: DatabaseManager, dp: Dispatcher = None):
        self.config_manager = config_manager
        self.db = db
        self.dp = dp
        self.registry = PluginRegistry()
        self.logger = LoggingManager().get_logger(__name__)

        # Храним состояние плагинов
        self.loaded_plugins: Dict[str, PluginBase] = {}
        self.plugin_states: Dict[str, bool] = {}
        self.plugin_routers: Dict[str, Router] = {}

        # ВАЖНО: Явно импортируем плагины для регистрации
        self._import_plugins()

    def _import_plugins(self):
        """Явно импортирует все плагины для их регистрации"""
        import os
        plugins_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'plugins')

        if not os.path.exists(plugins_dir):
            self.logger.warning(f"Plugins directory not found: {plugins_dir}")
            return

        for item in os.listdir(plugins_dir):
            plugin_path = os.path.join(plugins_dir, item)

            if (os.path.isdir(plugin_path) and
                    not item.startswith('_') and
                    not item.startswith('.') and
                    item != '__pycache__'):

                plugin_init = os.path.join(plugin_path, "__init__.py")
                if os.path.exists(plugin_init):
                    try:
                        # Импортируем плагин для его регистрации
                        importlib.import_module(f"plugins.{item}")
                        self.logger.debug(f"Imported plugin: {item}")
                    except Exception as e:
                        self.logger.error(f"Failed to import plugin {item}: {e}")

    def load_all(self) -> Dict[str, PluginBase]:
        """
        Загружает все плагины и сохраняет их состояние
        """
        plugins_map = {}
        factories = self.registry.get_all()

        self.logger.info(f"Found {len(factories)} registered plugins: {list(factories.keys())}")

        # ЕСЛИ НЕТ ЗАРЕГИСТРИРОВАННЫХ ПЛАГИНОВ - пробуем найти вручную
        if not factories:
            self.logger.warning("No plugins found in registry, trying manual discovery...")
            factories = self._discover_plugins_manually()

        for plugin_dir_name, factory in factories.items():
            try:
                # Проверяем конфиг плагина
                try:
                    config_module = importlib.import_module(f"plugins.{plugin_dir_name}.config")
                    enabled = getattr(config_module, 'ENABLED', True)
                except (ModuleNotFoundError, ImportError):
                    enabled = True

                if not enabled:
                    self.logger.info(f"Plugin {plugin_dir_name.upper()} disabled via config.ENABLED")
                    self.plugin_states[plugin_dir_name.upper()] = False
                    continue

                # Создаем экземпляр плагина
                plugin = factory(self.config_manager, self.db)
                plugin_name = plugin.get_name()

                plugins_map[plugin_name] = plugin
                self.loaded_plugins[plugin_name] = plugin
                self.plugin_states[plugin_name] = True

                # Сохраняем роутер
                self.plugin_routers[plugin_name] = plugin.get_router()

                self._register_plugin_models(plugin_dir_name)
                self.logger.info(f"Plugin {plugin_name} loaded and enabled")

            except Exception as e:
                self.logger.error(f"Failed to load plugin {plugin_dir_name}: {e}")
                continue

        self.logger.info(f"Final state: {len(self.loaded_plugins)} loaded plugins: {list(self.loaded_plugins.keys())}")
        self.logger.info(f"Final plugin_states: {self.plugin_states}")

        return plugins_map

    def _discover_plugins_manually(self) -> Dict:
        """Ручное обнаружение плагинов если регистрация не сработала"""
        import os
        plugins_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'plugins')
        discovered_plugins = {}

        if not os.path.exists(plugins_dir):
            return discovered_plugins

        for item in os.listdir(plugins_dir):
            plugin_path = os.path.join(plugins_dir, item)

            if (os.path.isdir(plugin_path) and
                    not item.startswith('_') and
                    not item.startswith('.') and
                    item != '__pycache__'):

                plugin_init = os.path.join(plugin_path, "__init__.py")
                if os.path.exists(plugin_init):
                    try:
                        # Пытаемся импортировать и создать плагин вручную
                        plugin_module = importlib.import_module(f"plugins.{item}")

                        # Ищем класс плагина
                        for attr_name in dir(plugin_module):
                            attr = getattr(plugin_module, attr_name)
                            if (isinstance(attr, type) and
                                    issubclass(attr, PluginBase) and
                                    attr != PluginBase):
                                # Создаем фабрику для этого плагина
                                def make_factory(plugin_class):
                                    return lambda config, db: plugin_class(config, db)

                                discovered_plugins[item] = make_factory(attr)
                                self.logger.info(f"Manually discovered plugin: {item}")
                                break

                    except Exception as e:
                        self.logger.error(f"Failed to manually discover plugin {item}: {e}")

        return discovered_plugins

    async def enable_plugin(self, plugin_name: str) -> bool:
        """
        Включает плагин (добавляет его роутер в диспетчер)
        """
        try:
            if plugin_name not in self.loaded_plugins:
                self.logger.error(f"Plugin {plugin_name} not found")
                return False

            if self.plugin_states.get(plugin_name, False):
                self.logger.info(f"Plugin {plugin_name} is already enabled")
                return True

            # Добавляем роутер в диспетчер
            if self.dp and plugin_name in self.plugin_routers:
                self.dp.include_router(self.plugin_routers[plugin_name])
                self.logger.info(f"Plugin {plugin_name} router added to dispatcher")

            self.plugin_states[plugin_name] = True
            self.logger.info(f"Plugin {plugin_name} enabled")
            return True

        except Exception as e:
            self.logger.error(f"Error enabling plugin {plugin_name}: {e}")
            return False

    async def disable_plugin(self, plugin_name: str) -> bool:
        """
        Выключает плагин (удаляет его роутер из диспетчера)
        """
        try:
            if plugin_name not in self.loaded_plugins:
                self.logger.error(f"Plugin {plugin_name} not found")
                return False

            if not self.plugin_states.get(plugin_name, True):
                self.logger.info(f"Plugin {plugin_name} is already disabled")
                return True

            # NOTE: В aiogram 3.x нет прямого метода удаления роутера
            # Временно просто помечаем как выключенный
            # Для реального удаления нужно перезапустить бота или использовать более сложную логику

            self.plugin_states[plugin_name] = False
            self.logger.info(f"Plugin {plugin_name} disabled (router remains for current session)")
            return True

        except Exception as e:
            self.logger.error(f"Error disabling plugin {plugin_name}: {e}")
            return False

    def get_plugin_info(self, plugin_name: str) -> Dict:
        """
        Возвращает информацию о плагине
        """
        plugin = self.loaded_plugins.get(plugin_name)
        if not plugin:
            return {}

        try:
            settings = plugin.get_settings()
            router = plugin.get_router()

            # УПРОЩЕННЫЙ подсчет обработчиков - безопасный способ
            handler_count = 0
            if router:
                try:
                    # Безопасный подсчет через атрибуты роутера
                    if hasattr(router, 'message') and hasattr(router.message, 'handlers'):
                        handler_count += len(router.message.handlers)
                    if hasattr(router, 'callback_query') and hasattr(router.callback_query, 'handlers'):
                        handler_count += len(router.callback_query.handlers)
                    # Добавляем другие типы обработчиков если нужно
                except Exception as count_error:
                    self.logger.debug(f"Error counting handlers for {plugin_name}: {count_error}")
                    # Если не получается посчитать, ставим 0

            return {
                "name": plugin_name,
                "enabled": self.plugin_states.get(plugin_name, True),
                "display_name": getattr(settings, 'PLUGIN_TITLE', plugin_name),
                "description": getattr(settings, 'PLUGIN_DESCRIPTION', 'No description'),
                "has_router": router is not None,
                "handler_count": handler_count,
                "version": getattr(plugin, 'version', '1.0.0')
            }
        except Exception as e:
            self.logger.error(f"Error getting plugin info for {plugin_name}: {e}")
            # ВОЗВРАЩАЕМ базовую информацию даже при ошибке
            return {
                "name": plugin_name,
                "enabled": self.plugin_states.get(plugin_name, True),
                "display_name": plugin_name,
                "description": "Error loading plugin info",
                "has_router": False,
                "handler_count": 0,
                "error": str(e)
            }

    def get_plugins_list(self) -> List[Dict]:
        """
        Возвращает список всех плагинов
        """
        plugins_info = []
        for plugin_name in self.loaded_plugins.keys():
            plugin_info = self.get_plugin_info(plugin_name)
            plugins_info.append(plugin_info)

        return plugins_info

    def is_plugin_enabled(self, plugin_name: str) -> bool:
        """
        Проверяет включен ли плагин
        """
        return self.plugin_states.get(plugin_name, False)

    def get_enabled_plugins(self) -> List[str]:
        """
        Возвращает список включенных плагинов
        """
        return [name for name, enabled in self.plugin_states.items() if enabled]

    def get_disabled_plugins(self) -> List[str]:
        """
        Возвращает список выключенных плагинов
        """
        return [name for name, enabled in self.plugin_states.items() if not enabled]

    def _register_plugin_models(self, plugin_name: str):
        """Автоматически импортирует модели плагина для регистрации в БД"""
        try:
            importlib.import_module(f"plugins.{plugin_name}.models")
        except ModuleNotFoundError:
            pass
        except Exception as e:
            self.logger.error(f"Failed to register plugin models '{plugin_name}': {e}")

import importlib
from core.bot.logging import logger
from core.config import ConfigManager
from databases import DatabaseManager
from .registry import get_registered_plugins
from .base import PluginBase


class PluginManager:
    """
    Менеджер для загрузки и управления плагинами
    """

    def __init__(self, config_manager: ConfigManager, db: DatabaseManager):
        self.config_manager = config_manager
        self.db = db

    def load_all(self) -> dict[str, PluginBase]:
        """
        Загружает все зарегистрированные плагины
        """
        plugins_map = {}
        factories = get_registered_plugins()

        logger.info(f"Found {len(factories)} registered plugins: {list(factories.keys())}")

        for plugin_dir_name, factory in factories.items():
            try:
                plugin = factory(self.config_manager, self.db)
                plugin_name = plugin.get_name()

                settings = plugin.get_settings()
                try:
                    config_module = importlib.import_module(f"plugins.{plugin_dir_name}.config")
                    enabled = getattr(config_module, 'ENABLED', True)
                except (ModuleNotFoundError, ImportError) as e:
                    logger.warning(f"Plugin {plugin_name} config module not found, using default ENABLED=True")
                    enabled = True

                logger.debug(f"Plugin {plugin_name} enabled status from config: {enabled}")

                if not enabled:
                    logger.info(f"Plugin {plugin_name} DISABLED via config.ENABLED=False")
                    continue

                plugins_map[plugin_name] = plugin
                self._register_plugin_models(plugin_dir_name)
                logger.info(f"Plugin {plugin_name} ENABLED (dir: {plugin_dir_name})")

            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_dir_name}: {e}")
                continue

        logger.info(f"Successfully loaded {len(plugins_map)} plugins: {list(plugins_map.keys())}")
        return plugins_map

    def _register_plugin_models(self, plugin_name: str):
        """Автоматически импортирует модели плагина для регистрации в БД"""
        try:
            importlib.import_module(f"plugins.{plugin_name}.models")
            logger.debug(f"Plugin database models registered: {plugin_name}")
        except ModuleNotFoundError:
            pass
        except Exception as e:
            logger.error(f"Failed to register plugin models '{plugin_name}': {e}")

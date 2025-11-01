import importlib
from core.config import ConfigManager
from modules.databases import DatabaseManager
from core.plugins.global_registry import plugin_registry
from core.plugins.base import PluginBase
from core.logging import LoggingManager


class PluginManager:
    """
    Менеджер для загрузки и управления плагинами
    """

    def __init__(self, config_manager: ConfigManager, db: DatabaseManager):
        self.config_manager = config_manager
        self.db = db
        self.registry = plugin_registry
        self.logger = LoggingManager().get_logger(__name__)

    def load_all(self) -> dict[str, PluginBase]:
        """
        Загружает все зарегистрированные плагины
        """
        plugins_map = {}
        factories = self.registry.get_all()

        self.logger.info(f"Found {len(factories)} registered plugins: {list(factories.keys())}")

        for plugin_dir_name, factory in factories.items():
            try:
                try:
                    config_module = importlib.import_module(f"plugins.{plugin_dir_name}.config")
                    enabled = getattr(config_module, 'ENABLED', True)
                except (ModuleNotFoundError, ImportError):
                    enabled = True

                if not enabled:
                    self.logger.info(f"Plugin {plugin_dir_name.upper()} disabled via config.ENABLED")
                    continue

                plugin = factory(self.config_manager, self.db)
                plugin_name = plugin.get_name()

                plugins_map[plugin_name] = plugin
                self._register_plugin_models(plugin_dir_name)
                self.logger.info(f"Plugin {plugin_name} enabled")

            except Exception as e:
                self.logger.error(f"Failed to load plugin {plugin_dir_name}: {e}")
                continue

        return plugins_map

    def _register_plugin_models(self, plugin_name: str):
        """Автоматически импортирует модели плагина для регистрации в БД"""
        try:
            importlib.import_module(f"plugins.{plugin_name}.models")
        except ModuleNotFoundError:
            pass
        except Exception as e:
            self.logger.error(f"Failed to register plugin models '{plugin_name}': {e}")

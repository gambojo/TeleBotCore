import os
import importlib
from core.logging import LoggingManager

logger = LoggingManager().get_logger(__name__)


def auto_register_plugins():
    """Автоматически регистрирует все плагины из папки plugins"""
    plugins_dir = os.path.dirname(__file__)

    logger.info(f"Scanning plugins directory: {plugins_dir}")

    for item in os.listdir(plugins_dir):
        plugin_path = os.path.join(plugins_dir, item)

        if (os.path.isdir(plugin_path) and
                not item.startswith('_') and
                not item.startswith('.')):

            plugin_init = os.path.join(plugin_path, "__init__.py")
            if os.path.exists(plugin_init):
                try:
                    # Импортируем модуль плагина
                    plugin_module = importlib.import_module(f"plugins.{item}")
                    logger.info(f"Successfully imported plugin: {item}")
                except Exception as e:
                    logger.error(f"Failed to import plugin {item}: {e}")


# Автоматически регистрируем при импорте
auto_register_plugins()

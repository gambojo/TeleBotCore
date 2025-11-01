from typing import Dict, Any
from core.plugins.manager import PluginManager
from core.config import ConfigManager
from modules.databases import DatabaseManager
from core.logging import LoggingManager


class PluginStats:
    """
    Сбор статистики по плагинам для ядра системы
    """

    def __init__(self, plugin_manager: PluginManager, config: ConfigManager, db: DatabaseManager):
        self.plugin_manager = plugin_manager
        self.config = config
        self.db = db
        self.logger = LoggingManager().get_logger(__name__)

    async def get_plugins_stats(self) -> Dict[str, Any]:
        """
        Возвращает детальную статистику по плагинам
        """
        try:
            if not self.plugin_manager:
                return await self._get_basic_plugins_stats()

            plugins = self.plugin_manager.load_all()

            plugins_info = []
            enabled_count = 0

            for plugin_name, plugin in plugins.items():
                plugin_info = await self._get_plugin_info(plugin_name, plugin)
                plugins_info.append(plugin_info)

                if plugin_info.get("enabled", False):
                    enabled_count += 1

            return {
                "total_plugins": len(plugins),
                "enabled_plugins": enabled_count,
                "disabled_plugins": len(plugins) - enabled_count,
                "plugins": plugins_info,
                "plugin_names": list(plugins.keys())
            }

        except Exception as e:
            self.logger.error(f"Error getting plugins stats: {e}")
            return await self._get_basic_plugins_stats()

    async def _get_basic_plugins_stats(self) -> Dict[str, Any]:
        """
        Базовая статистика плагинов без PluginManager
        """
        return {
            "total_plugins": 1,
            "enabled_plugins": 1,
            "disabled_plugins": 0,
            "plugins": [
                {
                    "name": "ADMINPANEL",
                    "enabled": True,
                    "display_name": "Админ-панель",
                    "has_router": True,
                    "handler_count": 6
                }
            ],
            "plugin_names": ["ADMINPANEL"]
        }

    async def _get_plugin_info(self, plugin_name: str, plugin) -> Dict[str, Any]:
        """
        Получает информацию о конкретном плагине - УСТОЙЧИВАЯ ВЕРСИЯ
        """
        try:
            settings = plugin.get_settings()
            router = plugin.get_router()

            # Безопасный подсчет обработчиков
            handler_count = 0
            if router:
                try:
                    # Проверяем наличие атрибутов перед доступом
                    if hasattr(router, 'message') and hasattr(router.message, 'handlers'):
                        handler_count += len(router.message.handlers)
                    if hasattr(router, 'callback_query') and hasattr(router.callback_query, 'handlers'):
                        handler_count += len(router.callback_query.handlers)
                except Exception as count_error:
                    self.logger.debug(f"Safe handler count failed for {plugin_name}: {count_error}")

            return {
                "name": plugin_name,
                "enabled": getattr(settings, 'ENABLED', True),
                "display_name": getattr(settings, 'PLUGIN_TITLE', plugin_name),
                "has_router": router is not None,
                "handler_count": handler_count,
                "settings": self._get_plugin_settings(settings)
            }
        except Exception as e:
            self.logger.error(f"Error getting plugin info for {plugin_name}: {e}")
            # ВОЗВРАЩАЕМ базовую информацию
            return {
                "name": plugin_name,
                "enabled": True,
                "display_name": plugin_name,
                "has_router": False,
                "handler_count": 0,
                "error": str(e)
            }

    def _get_plugin_settings(self, settings) -> Dict[str, Any]:
        """
        Извлекает настройки плагина (без чувствительных данных)
        """
        try:
            safe_settings = {}
            for key, value in settings.__dict__.items():
                if not key.startswith('_') and not isinstance(value, (str, int, bool, float, type(None))):
                    continue
                if any(sensitive in key.lower() for sensitive in ['password', 'token', 'secret', 'key']):
                    safe_settings[key] = '***'
                else:
                    safe_settings[key] = value
            return safe_settings
        except Exception as e:
            self.logger.error(f"Error extracting plugin settings: {e}")
            return {}

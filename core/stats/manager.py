from typing import Dict, Any
from core.config import ConfigManager
from modules.databases import DatabaseManager
from core.plugins.manager import PluginManager
from .plugins import PluginStats
from .system import SystemStats
from core.logging import LoggingManager


class StatsManager:
    """
    Менеджер статистики для сбора всех видов статистики системы
    """

    def __init__(self, config: ConfigManager, db: DatabaseManager, plugin_manager: PluginManager):
        self.config = config
        self.db = db
        self.plugin_manager = plugin_manager
        self.logger = LoggingManager().get_logger(__name__)

        # Инициализируем сборщики статистики
        self.plugin_stats = PluginStats(plugin_manager, config, db)
        self.system_stats = SystemStats(config, db)

    async def get_comprehensive_stats(self) -> Dict[str, Any]:
        """
        Возвращает комплексную статистику системы
        """
        try:
            plugin_stats = await self.plugin_stats.get_plugins_stats()
            system_stats = await self.system_stats.get_system_stats()

            return {
                "plugins": plugin_stats,
                "system": system_stats,
                "timestamp": "current_time_here"
            }
        except Exception as e:
            self.logger.error(f"Error getting comprehensive stats: {e}")
            return {
                "plugins": {},
                "system": {},
                "error": str(e)
            }

    async def get_plugins_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику по плагинам
        """
        return await self.plugin_stats.get_plugins_stats()

    async def get_system_stats(self) -> Dict[str, Any]:
        """
        Возвращает системную статистику
        """
        return await self.system_stats.get_system_stats()

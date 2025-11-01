from typing import Dict, Any
from core.config import ConfigManager
from modules.databases import DatabaseManager, UserManager
from core.logging import LoggingManager
import psutil
import os


class SystemStats:
    """
    Сбор системной статистики для ядра
    """

    def __init__(self, config: ConfigManager, db: DatabaseManager):
        self.config = config
        self.db = db
        self.user_manager = UserManager()
        self.logger = LoggingManager().get_logger(__name__)

    async def get_system_stats(self) -> Dict[str, Any]:
        """
        Возвращает комплексную системную статистику
        """
        try:
            user_stats = await self._get_user_stats()
            memory_stats = await self._get_memory_stats()
            database_stats = await self._get_database_stats()
            rbac_stats = await self._get_rbac_stats()

            return {
                "users": user_stats,
                "memory": memory_stats,
                "database": database_stats,
                "rbac": rbac_stats,
                "bot": await self._get_bot_stats()
            }

        except Exception as e:
            self.logger.error(f"Error getting system stats: {e}")
            return {
                "users": {"error": str(e)},
                "memory": {"error": str(e)},
                "database": {"error": str(e)},
                "rbac": {"error": str(e)},
                "bot": {"error": str(e)}
            }

    async def _get_user_stats(self) -> Dict[str, Any]:
        """
        Статистика пользователей с исправленными данными по ролям из RBAC
        """
        try:
            total_users = await self.user_manager.get_user_count()

            # Получаем статистику по ролям из RBAC
            users_by_role = await self._get_users_by_role_from_rbac()

            return {
                "total_users": total_users,
                "users_by_role": users_by_role,
                "admin_count": len(self.config.settings.admin_ids)
            }
        except Exception as e:
            self.logger.error(f"Error getting user stats: {e}")
            return {"error": str(e)}

    async def _get_users_by_role_from_rbac(self) -> Dict[str, int]:
        """
        Возвращает статистику пользователей по ролям из RBAC системы
        """
        try:
            from core.auth import AuthManager
            auth = AuthManager(self.config)

            # Получаем всех пользователей
            all_users = await self.user_manager.get_all_users()

            # Считаем пользователей по ролям из RBAC
            role_stats = {}

            for user in all_users:
                user_roles = await auth.get_user_roles(user.telegram_id)

                if not user_roles:
                    # Если нет ролей в RBAC, считаем как user
                    role_stats["user"] = role_stats.get("user", 0) + 1
                else:
                    # Используем самую высокую роль для статистики
                    if "super_admin" in user_roles:
                        role_stats["super_admin"] = role_stats.get("super_admin", 0) + 1
                    elif "admin" in user_roles:
                        role_stats["admin"] = role_stats.get("admin", 0) + 1
                    else:
                        # Если есть другие роли, используем первую
                        primary_role = user_roles[0]
                        role_stats[primary_role] = role_stats.get(primary_role, 0) + 1

            self.logger.info(f"RBAC role statistics: {role_stats}")
            return role_stats

        except Exception as e:
            self.logger.error(f"Error getting RBAC role stats: {e}")
            # Fallback: возвращаем базовую статистику
            return {"user": await self.user_manager.get_user_count()}

    async def _get_memory_stats(self) -> Dict[str, Any]:
        """
        Статистика использования памяти
        """
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()

            return {
                "memory_used_mb": round(memory_info.rss / 1024 / 1024, 2),
                "memory_percent": round(process.memory_percent(), 2),
                "system_memory_percent": round(psutil.virtual_memory().percent, 2)
            }
        except Exception as e:
            self.logger.error(f"Error getting memory stats: {e}")
            return {"error": "Memory stats unavailable"}

    async def _get_database_stats(self) -> Dict[str, Any]:
        """
        Статистика базы данных
        """
        try:
            test_count = await self.user_manager.get_user_count()

            return {
                "status": "connected",
                "test_query_successful": True,
                "url": self._mask_database_url(self.config.settings.DATABASE_URL)
            }
        except Exception as e:
            self.logger.error(f"Error getting database stats: {e}")
            return {
                "status": "disconnected",
                "test_query_successful": False,
                "error": str(e)
            }

    async def _get_rbac_stats(self) -> Dict[str, Any]:
        """
        Статистика RBAC системы
        """
        try:
            from core.rbac import RBACManager
            rbac = RBACManager(self.db)

            test_user_id = list(self.config.settings.admin_ids)[0] if self.config.settings.admin_ids else 0
            rbac_working = False

            if test_user_id:
                rbac_working = await rbac.user_has_permission(test_user_id, "admin_panel.access")

            return {
                "enabled": True,
                "working": rbac_working,
                "test_user_id": test_user_id
            }
        except Exception as e:
            self.logger.error(f"Error getting RBAC stats: {e}")
            return {
                "enabled": False,
                "working": False,
                "error": str(e)
            }

    async def _get_bot_stats(self) -> Dict[str, Any]:
        """
        Статистика бота
        """
        try:
            from core.version import VersionManager
            version_manager = VersionManager()

            return {
                "version": version_manager.version,
                "title": version_manager.title,
                "admin_count": len(self.config.settings.admin_ids),
                "support_username": self.config.settings.SUPPORT
            }
        except Exception as e:
            self.logger.error(f"Error getting bot stats: {e}")
            return {"error": str(e)}

    def _mask_database_url(self, url: str) -> str:
        """
        Маскирует чувствительные данные в URL базы данных
        """
        if "://" in url:
            protocol, rest = url.split("://", 1)
            if "@" in rest:
                auth, host = rest.split("@", 1)
                if ":" in auth:
                    user, password = auth.split(":", 1)
                    return f"{protocol}://{user}:***@{host}"
            return f"{protocol}://{rest}"
        return "***"

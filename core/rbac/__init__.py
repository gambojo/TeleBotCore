from .manager import RBACManager
from .permissions import SystemPermissions


# Временные заглушки для избежания циклических импортов
class RBACManager:
    """Заглушка RBAC менеджера"""

    def __init__(self, db):
        self.db = db
        from core.logging import LoggingManager
        self.logger = LoggingManager().get_logger(__name__)

    async def user_has_permission(self, user_id: int, permission: str) -> bool:
        """Заглушка - всегда True для админов"""
        from core.config import ConfigManager
        config = ConfigManager()
        return user_id in config.settings.admin_ids

    async def get_user_roles(self, user_id: int) -> list:
        """Заглушка - возвращает базовые роли"""
        from core.config import ConfigManager
        config = ConfigManager()
        if user_id in config.settings.admin_ids:
            return ["super_admin"]
        return ["user"]

    async def initialize_system(self):
        """Заглушка инициализации"""
        self.logger.info("RBAC system initialized (stub)")

    async def initialize_default_roles(self):
        """Заглушка инициализации ролей"""
        pass

    async def assign_role_to_user(self, user_id: int, role_name: str) -> bool:
        """Заглушка назначения роли"""
        return True

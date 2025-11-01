from core.config import ConfigManager
from modules.databases import DatabaseManager
from core.rbac import RBACManager
from typing import List


class AuthManager:
    """
    Упрощенный менеджер аутентификации для работы с RBAC
    """

    def __init__(self, config_manager: ConfigManager = None):
        self.config = config_manager or ConfigManager()
        self.db = DatabaseManager()
        self.rbac = RBACManager(self.db)

    async def is_admin(self, telegram_id: int) -> bool:
        """Проверяет является ли пользователь администратором через RBAC"""
        return await self.rbac.user_has_permission(telegram_id, "admin_panel.access")

    async def check_permission(self, telegram_id: int, permission: str) -> bool:
        """Проверяет разрешение через RBAC"""
        return await self.rbac.user_has_permission(telegram_id, permission)

    async def get_user_roles(self, telegram_id: int) -> List[str]:
        """Возвращает роли пользователя"""
        return await self.rbac.get_user_roles(telegram_id)

    async def assign_admin_role(self, telegram_id: int) -> bool:
        """Назначает роль администратора"""
        return await self.rbac.assign_role_to_user(telegram_id, "admin")

    async def remove_admin_role(self, telegram_id: int) -> bool:
        """Удаляет роль администратора"""
        return await self.rbac.remove_user_role(telegram_id, "admin")

    async def user_has_role(self, telegram_id: int, role_name: str) -> bool:
        """Проверяет, есть ли у пользователя указанная роль"""
        user_roles = await self.get_user_roles(telegram_id)
        return role_name in user_roles

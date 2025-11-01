from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from typing import Union, Any, Dict
from modules.databases import DatabaseManager
from core.rbac import RBACManager


class HasPermissionFilter(BaseFilter):
    """Фильтр для проверки RBAC разрешений"""

    def __init__(self, permission: str):
        self.permission = permission

    async def __call__(
            self,
            update: Union[Message, CallbackQuery],
            **data: Any
    ) -> bool:
        """Проверяет разрешение через RBAC"""
        db: DatabaseManager = data.get("db")
        if not db:
            return False

        rbac = RBACManager(db)
        user_id = update.from_user.id
        return await rbac.user_has_permission(user_id, self.permission)


class HasRoleFilter(BaseFilter):
    """Фильтр для проверки RBAC ролей"""

    def __init__(self, role: str):
        self.role = role

    async def __call__(
            self,
            update: Union[Message, CallbackQuery],
            **data: Any
    ) -> bool:
        """Проверяет роль через RBAC"""
        db: DatabaseManager = data.get("db")
        if not db:
            return False

        rbac = RBACManager(db)
        user_id = update.from_user.id
        user_roles = await rbac.get_user_roles(user_id)
        return self.role in user_roles


class AdminPanelAccessFilter(BaseFilter):
    """Фильтр для доступа к админ-панели"""

    async def __call__(
            self,
            update: Union[Message, CallbackQuery],
            **data: Any
    ) -> bool:
        """Проверяет доступ к админ-панели"""
        db: DatabaseManager = data.get("db")
        if not db:
            return False

        rbac = RBACManager(db)
        user_id = update.from_user.id
        return await rbac.user_has_permission(user_id, "admin_panel.access")

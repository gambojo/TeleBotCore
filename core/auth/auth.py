from core.config import ConfigManager
from modules.databases import DatabaseManager
from core.rbac import RBACManager
from typing import List


class AuthManager:
    """
    Менеджер аутентификации и авторизации пользователей
    """

    def __init__(self, config_manager: ConfigManager = None):
        self.config = config_manager or ConfigManager()
        self.db = DatabaseManager()
        self.rbac = RBACManager(self.db)

    def determine_role(self, telegram_id: int) -> str:
        """
        Определяет роль пользователя по его Telegram ID
        """
        if telegram_id in self.config.settings.admin_ids:
            return "admin"
        return "user"

    def is_admin(self, telegram_id: int) -> bool:
        """
        Проверяет является ли пользователь администратором
        """
        return self.determine_role(telegram_id) == "admin"

    def get_admin_ids(self) -> list[int]:
        """
        Возвращает список ID администраторов
        """
        return self.config.settings.admin_ids

    async def check_permission(self, telegram_id: int, permission: str) -> bool:
        """
        Проверяет разрешение через RBAC
        """
        return await self.rbac.user_has_permission(telegram_id, permission)

    async def get_user_permissions(self, telegram_id: int) -> List[str]:
        """
        Возвращает все разрешения пользователя
        """
        # Получаем роли пользователя
        user_roles = await self.rbac.get_user_roles(telegram_id)

        # Собираем все уникальные разрешения из всех ролей
        all_permissions = set()
        session = self.db.create_session()

        try:
            async with session:
                from core.rbac.models import RBACRole
                from sqlalchemy import select

                for role_name in user_roles:
                    result = await session.execute(
                        select(RBACRole).where(RBACRole.name == role_name)
                    )
                    role = result.scalar_one_or_none()
                    if role:
                        for permission in role.permissions:
                            all_permissions.add(permission.name)

                return list(all_permissions)

        except Exception as e:
            self.rbac.logger.error(f"Error getting user permissions: {e}")
            return []


# Для обратной совместимости со старым кодом
_auth_manager = AuthManager()
determine_role = _auth_manager.determine_role

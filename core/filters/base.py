from aiogram.filters import BaseFilter
from aiogram.types import Message
from databases import UserManager


class DatabaseFilter(BaseFilter):
    """
    Базовый фильтр с инжектированным UserManager
    Параметры: user_manager - менеджер пользователей
    Возвращает: экземпляр DatabaseFilter
    Пример: filter = DatabaseFilter(user_manager)
    """

    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager


class RoleFilter(DatabaseFilter):
    """
    Фильтр для проверки роли пользователя
    Параметры: user_manager - менеджер пользователей, required_role - требуемая роль
    Возвращает: bool - True если роль совпадает
    Пример: @router.message(RoleFilter(user_manager, 'admin'))
    """

    def __init__(self, user_manager: UserManager, required_role: str):
        super().__init__(user_manager)
        self.required_role = required_role

    async def __call__(self, msg: Message) -> bool:
        user = await self.user_manager.get(msg.from_user.id)
        return getattr(user, "role", None) == self.required_role


class PermissionFilter(DatabaseFilter):
    """
    Фильтр для проверки прав пользователя
    Параметры: user_manager - менеджер пользователей, is_admin, is_verified, is_active - флаги
    Возвращает: bool - True если пользователь соответствует условиям
    Пример: @router.message(PermissionFilter(user_manager, is_admin=True))
    """

    def __init__(self, user_manager: UserManager, *, is_admin: bool = None, is_verified: bool = None,
                 is_active: bool = None):
        super().__init__(user_manager)
        self.flags = {
            "is_admin": is_admin,
            "is_verified": is_verified,
            "is_active": is_active,
        }

    async def __call__(self, msg: Message) -> bool:
        user = await self.user_manager.get(msg.from_user.id)
        if not user:
            return False

        for attr, expected in self.flags.items():
            if expected is not None and getattr(user, attr, None) != expected:
                return False

        return True


class GroupFilter(BaseFilter):
    """
    Фильтр для проверки доступа к групповым чатам
    Параметры: allowed_chat_ids - список разрешенных ID чатов
    Возвращает: bool - True если чат разрешен
    Пример: @router.message(GroupFilter([-100123456]))
    """

    def __init__(self, allowed_chat_ids: list[int]):
        self.allowed_chat_ids = allowed_chat_ids

    async def __call__(self, msg: Message) -> bool:
        chat_id = msg.chat.id
        return chat_id in self.allowed_chat_ids

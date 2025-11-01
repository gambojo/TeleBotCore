from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Message, CallbackQuery
from modules.databases import UserManager
from core.logging import LoggingManager


class UserInitMiddleware(BaseMiddleware):
    """Упрощенный middleware для инициализации пользователя"""

    def __init__(self):
        self.user_manager = UserManager()
        self.logger = LoggingManager().get_logger(__name__)

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        """Обрабатывает обновление и инициализирует пользователя"""
        try:
            user_data = event.from_user

            # Сохраняем пользователя в БД (только базовые данные)
            user, is_new = await self.user_manager.ensure(
                telegram_id=user_data.id,
                username=user_data.username,
                first_name=user_data.first_name,
                last_name=user_data.last_name
            )

            data["user"] = user
            data["is_new_user"] = is_new

            return await handler(event, data)

        except Exception as e:
            self.logger.error(f"Error in UserInitMiddleware: {e}")
            # Продолжаем выполнение даже при ошибке
            return await handler(event, data)

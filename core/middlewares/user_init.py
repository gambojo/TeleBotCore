from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message, TelegramObject
from databases import UserManager


class UserInitMiddleware(BaseMiddleware):
    """
    Middleware для инициализации пользователя в данных запроса
    """

    def __init__(self):
        super().__init__()

    async def __call__(self, handler, event: TelegramObject, data: dict):
        if isinstance(event, Message) and event.from_user:
            try:
                # Создаем UserManager для каждого запроса
                user_manager = UserManager()
                user, _ = await user_manager.ensure(
                    telegram_id=event.from_user.id,
                    username=event.from_user.username,
                    first_name=event.from_user.first_name,
                    last_name=event.from_user.last_name
                )
                data["user"] = user
            except Exception as e:
                from core.bot.logging import logger
                logger.error(f"Error in UserInitMiddleware: {e}")
                data["user"] = None

        return await handler(event, data)

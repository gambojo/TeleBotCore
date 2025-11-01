from core.logging import LoggingManager
import traceback
from aiogram import Router
from aiogram.types import ErrorEvent


class ErrorHandler:
    """
    Глобальный обработчик ошибок бота
    """

    def __init__(self):
        self.logger = LoggingManager().get_logger(__name__)
        self.router = Router(name="error_handler")
        self._register_handlers()

    def _register_handlers(self):
        """Приватный метод для регистрации хендлеров в роутере"""
        self.router.errors.register(self.handle_errors)

    def get_router(self) -> Router:
        """Возвращает готовый роутер с зарегистрированными хендлерами"""
        return self.router

    async def handle_errors(self, event: ErrorEvent):
        """Глобальный обработчик ошибок бота"""
        exc = event.exception
        self.logger.error("Ошибка: %s", exc)
        traceback.print_exception(type(exc), exc, exc.__traceback__)

        msg = getattr(event.update, "message", None)
        if msg:
            if isinstance(exc, PermissionError):
                await msg.answer(str(exc))
            else:
                await msg.answer("Произошла ошибка.")

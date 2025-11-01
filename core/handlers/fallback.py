from aiogram import Router, F
from aiogram.types import CallbackQuery


class FallbackHandler:
    """
    Обработчик для необработанных callback-запросов
    """

    def __init__(self):
        self.router = Router(name="fallback")
        self._register_handlers()

    def _register_handlers(self):
        """Приватный метод для регистрации хендлеров в роутере"""
        self.router.callback_query.register(self.unhandled_callback)

    def get_router(self) -> Router:
        """Возвращает готовый роутер с зарегистрированными хендлерами"""
        return self.router

    async def unhandled_callback(self, callback: CallbackQuery):
        """Обработчик для необработанных callback-запросов"""
        await callback.answer(f"Необработанный callback: {callback.data}", show_alert=True)

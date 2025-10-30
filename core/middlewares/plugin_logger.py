from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from core.logging import LoggingManager

class PluginLoggerMiddleware(BaseMiddleware):
    """
    Middleware для логирования событий плагинов
    Параметры: plugin_name - имя плагина для логирования
    Возвращает: экземпляр PluginLoggerMiddleware
    Пример: middleware = PluginLoggerMiddleware('VPN')
    """

    def __init__(self, plugin_name: str = "UnknownPlugin"):
        self.logger_manager = LoggingManager()
        self.logger = self.logger_manager.get_plugin_logger(plugin_name)

    async def __call__(self, handler, event, data):
        user_id = getattr(event.from_user, "id", "unknown")
        username = getattr(event.from_user, "username", "unknown")

        state: FSMContext = data.get("state")
        if state:
            current = await state.get_state()
            self.logger.debug(f"FSM state for {username} ({user_id}): {current}")

        if isinstance(event, Message):
            self.logger.info(f"Message from {username} ({user_id}): {event.text}")
        elif isinstance(event, CallbackQuery):
            self.logger.info(f"Callback from {username} ({user_id}): {event.data}")

        return await handler(event, data)

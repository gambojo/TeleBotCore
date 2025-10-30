import logging
import traceback
from aiogram import Router
from aiogram.types import ErrorEvent

router = Router(name="error_handler")
logger = logging.getLogger(__name__)

@router.errors()
async def handle_errors(event: ErrorEvent):
    """
    Глобальный обработчик ошибок бота
    Параметры: event - событие ошибки
    Возвращает: None
    Пример: автоматически вызывается при возникновении ошибки
    """
    exc = event.exception
    logger.error("Ошибка: %s", exc)
    traceback.print_exception(type(exc), exc, exc.__traceback__)

    msg = getattr(event.update, "message", None)
    if msg:
        if isinstance(exc, PermissionError):
            await msg.answer(str(exc))
        else:
            await msg.answer("Произошла ошибка.")

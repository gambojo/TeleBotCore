from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router(name="fallback")

@router.callback_query()
async def unhandled_callback(callback: CallbackQuery):
    """
    Обработчик для необработанных callback-запросов
    Параметры: callback - callback-запрос
    Возвращает: None
    Пример: автоматически вызывается для неизвестных callback_data
    """
    await callback.answer(f"Необработанный callback: {callback.data}", show_alert=True)

from aiogram import Router
from aiogram.types import CallbackQuery
from databases import DatabaseManager, UserManager
from core.display import ImageManager, HTMLBuilder
from core.keyboards import MainMenuKeyboard
from core.plugins import PluginBase

router = Router()


class CallbackHandler:
    """
    Обработчик callback-запросов для главного меню
    Параметры: db - менеджер БД, images - менеджер изображений, plugins - словарь плагинов
    Возвращает: экземпляр CallbackHandler
    Пример: handler = CallbackHandler(db, images, plugins)
    """

    def __init__(self, db: DatabaseManager, images: ImageManager, plugins: dict[str, PluginBase]):
        self.db = db
        self.images = images
        self.plugins = plugins

    def register(self, router: Router):
        """Регистрирует обработчики в роутере"""
        router.callback_query.register(self.handle_main_menu, lambda c: c.data == "main")

    async def handle_main_menu(self, callback: CallbackQuery):
        """Обрабатывает возврат в главное меню"""
        async with self.db.get_session() as session:
            user, _ = await UserManager(session).ensure(callback.from_user.id)

        banner = self.images.get_banner()
        text = HTMLBuilder().render_user(user).build()
        keyboard = MainMenuKeyboard(plugins=self.plugins).build()

        await callback.message.edit_caption(caption=text, reply_markup=keyboard, parse_mode="HTML")

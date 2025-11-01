from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from core.keyboards import MainMenuKeyboard
from core.display import ImageManager, HTMLBuilder
from modules.databases import UserManager
from core.config import ConfigManager
from core.logging import LoggingManager

router = Router()

class StartHandler:
    def __init__(self, images: ImageManager, plugins, config: ConfigManager):
        self.images = images
        self.plugins = plugins
        self.config = config
        self.router = Router()
        self._register_handlers()
        self.logger = LoggingManager().get_logger(__name__)

    def _register_handlers(self):
        """Приватный метод для регистрации хендлеров"""
        self.router.message.register(self.handle_start, CommandStart())
        self.router.callback_query.register(self.handle_main_menu, F.data.startswith("core:main_menu"))

    def get_router(self) -> Router:
        """Возвращает готовый роутер с зарегистрированными хендлерами"""
        return self.router

    async def handle_start(self, message: Message):
        """Обрабатывает команду /start"""
        await self._render_main_menu(message)

    async def handle_main_menu(self, callback: CallbackQuery):
        """Обрабатывает возврат в главное меню через callback"""
        try:
            # Всегда отправляем новое сообщение и удаляем старое
            await self._render_main_menu(callback.message, callback.from_user)
            try:
                await callback.message.delete()
            except:
                pass  # Игнорируем ошибки удаления
            await callback.answer()

        except Exception as e:
            self.logger.error(f"Error in main menu callback: {e}")
            await callback.answer("❌ Ошибка при загрузке меню", show_alert=True)

    async def _render_main_menu(self, message: Message, user_obj=None):
        """Отображает главное меню с пользователем и плагинами"""
        try:
            user_manager = UserManager()
            user_data = user_obj or message.from_user
            user, _ = await user_manager.ensure(
                telegram_id=user_data.id,
                username=user_data.username,
                first_name=user_data.first_name,
                last_name=user_data.last_name
            )

            banner = self.images.get_banner()
            text = HTMLBuilder().render_user(user).build()
            keyboard = MainMenuKeyboard(
                plugins=self.plugins,
                config=self.config
            ).build_markup()

            # Всегда отправляем новое сообщение
            await message.answer_photo(photo=banner, caption=text, reply_markup=keyboard, parse_mode="HTML")

        except Exception as e:
            self.logger.error(f"Error in main menu: {e}")
            await message.answer("❌ Произошла ошибка при загрузке меню. Попробуйте позже.")

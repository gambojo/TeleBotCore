from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from core.keyboards import MainMenuKeyboard
from core.display import ImageManager, HTMLBuilder
from databases import DatabaseManager, UserManager
from core.config import ConfigManager

router = Router()


class StartHandler:
    """
    Обработчик команды /start и главного меню
    """

    def __init__(self, db: DatabaseManager, images: ImageManager, plugins, config: ConfigManager):
        self.db = db
        self.images = images
        self.plugins = plugins
        self.config = config

    def register(self, dp):
        """Регистрирует обработчик команды /start"""
        dp.message.register(self.handle_start, CommandStart())

    async def handle_start(self, message: Message):
        """Обрабатывает команду /start"""
        await self._render_main_menu(message)

    async def _render_main_menu(self, message: Message):
        """Отображает главное меню с пользователем и плагинами"""
        try:
            user_manager = UserManager()
            user, _ = await user_manager.ensure(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )

            banner = self.images.get_banner()
            text = HTMLBuilder().render_user(user).build()
            keyboard = MainMenuKeyboard(
                plugins=self.plugins,
                config=self.config
            ).build_markup()

            await message.answer_photo(photo=banner, caption=text, reply_markup=keyboard, parse_mode="HTML")

        except Exception as e:
            from core.bot.logging import logger
            logger.error(f"Error in main menu: {e}")
            await message.answer("❌ Произошла ошибка при загрузке меню. Попробуйте позже.")

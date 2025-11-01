from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from core.keyboards import MainMenuKeyboard
from core.display import ImageManager, HTMLBuilder
from modules.databases import UserManager
from core.config import ConfigManager
from core.logging import LoggingManager
from core.auth import AuthManager

router = Router()

class StartHandler:
    def __init__(self, images: ImageManager, plugins, config: ConfigManager):
        self.images = images
        self.plugins = plugins
        self.config = config
        self.router = Router()
        self._register_handlers()
        self.logger = LoggingManager().get_logger(__name__)
        self.auth = AuthManager(config)

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
                pass
            await callback.answer()

        except Exception as e:
            self.logger.error(f"Error in main menu callback: {e}")
            await callback.answer("❌ Ошибка при загрузке меню", show_alert=True)

    def _get_integrated_buttons(self):
        """Возвращает интегрированные кнопки плагинов для главного меню"""
        try:
            integrated_buttons = []
            for name, plugin in self.plugins.items():
                try:
                    buttons = plugin.get_integrated_buttons()
                    if buttons:
                        integrated_buttons.extend(buttons)
                except Exception as e:
                    self.logger.error(f"Error getting buttons from plugin {name}: {e}")
                    continue
            return integrated_buttons
        except Exception as e:
            self.logger.error(f"Error in _get_integrated_buttons: {e}")
            return []

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

            # Получаем реальные роли из RBAC
            user_roles = await self.auth.get_user_roles(user.telegram_id)

            # Определяем отображаемую роль
            display_role = await self._get_display_role(user_roles)

            banner = self.images.get_banner()

            # Создаем текст с правильной ролью
            builder = HTMLBuilder()
            builder.title("👤 Профиль:")
            builder.field("Имя", user.first_name or "Не указано")
            builder.field("Id", str(user.telegram_id))
            builder.field("Роль", display_role)  # ← Используем роль из RBAC

            # Добавляем кнопки плагинов
            integrated_buttons = self._get_integrated_buttons()
            if integrated_buttons:
                builder.blank()
                builder.title("🧩 Плагины:")
                # Можно добавить информацию о плагинах если нужно
                # Например: builder.field("Доступно плагинов", str(len(self.plugins)))

            text = builder.build()
            keyboard = MainMenuKeyboard(
                plugins=self.plugins,
                config=self.config
            ).build_markup()

            # Всегда отправляем новое сообщение
            await message.answer_photo(photo=banner, caption=text, reply_markup=keyboard, parse_mode="HTML")

        except Exception as e:
            self.logger.error(f"Error in main menu: {e}")
            await message.answer("❌ Произошла ошибка при загрузке меню. Попробуйте позже.")

    async def _get_display_role(self, user_roles: list) -> str:
        """Определяет отображаемую роль на основе RBAC ролей"""
        if not user_roles:
            return "user 👤"

        if "super_admin" in user_roles:
            return "super_admin 👑"
        elif "admin" in user_roles:
            return "admin ⚙️"
        else:
            # Используем первую роль из списка
            return f"{user_roles[0]} 👤"

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from core.config import ConfigManager
from core.plugins import PluginManager, plugin_registry
from core.middlewares import UserInitMiddleware
from core.handlers.start import StartHandler
from core.display import ImageManager
from databases import DatabaseManager
from core.logging import LoggingManager
from core.auth import AuthManager
import plugins as loaded_plugins
from .version import version_manager


class BotApp:
    """
    Основной класс бота с исправленными зависимостями
    """
    def __init__(self):
        # 0️⃣ Логирование - ПЕРВЫМ делом!
        self.logging_manager = LoggingManager()
        self.logger = self.logging_manager.get_logger(__name__)
        self.logger.info("LoggingManager was loaded")

        # 1️⃣ Конфигурация
        self.config = ConfigManager()
        self.logger.info("ConfigManager was loaded")

        # 2️⃣ База данных
        self.db = DatabaseManager(self.config.settings.DATABASE_URL)
        self.logger.info("DatabaseManager was loaded")

        # 3️⃣ Изображения
        self.images = ImageManager(use_local=True)
        self.logger.info("ImageManager was loaded")

        # 4️⃣ Плагины
        self.plugin_registry = plugin_registry
        self.plugin_manager = PluginManager(config_manager=self.config, db=self.db)
        self.logger.info("PluginManager was loaded")
        self.loaded_plugins = loaded_plugins
        self.plugins = self.plugin_manager.load_all()
        # import plugins
        # self.logger.info(f"Loaded {len(self.plugins)} plugins: {list(self.plugins.keys())}")

        # 5️⃣ Стартовый хендлер
        self.start_handler = StartHandler(
            images=self.images,
            plugins=self.plugins,
            config=self.config
        )
        self.logger.info("StartHandler was loaded")

        # 6️⃣ Бот и диспетчер
        self.bot = Bot(token=self.config.settings.BOT_TOKEN,
                       default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.dp = Dispatcher(storage=MemoryStorage())

        # 7️⃣ Менеджер аутентификации
        self.auth_manager = AuthManager(self.config)
        self.logger.info("AuthManager was loaded")

        self.version_manager = version_manager

    async def run(self):
        """
        Запускает бота с правильным порядком загрузки роутеров
        """
        # Инициализация базы
        await self.db.init()
        self.logger.info("Database was initialized")

        # Middleware
        self.dp.message.middleware(UserInitMiddleware())
        self.logger.info("Middlewares was loaded")

        # 1️⃣ Сначала роутеры ЯДРА (важно!)
        self.dp.include_router(self.start_handler.get_router())

        # ErrorHandler
        from core.handlers.errors import ErrorHandler
        error_handler = ErrorHandler()
        self.dp.include_router(error_handler.get_router())

        self.logger.info("CoreRouters was loaded")

        # 2️⃣ Затем роутеры ПЛАГИНОВ
        for plugin in self.plugins.values():
            self.dp.include_router(plugin.get_router())
        self.logger.info("PluginRouters was loaded")

        # 3️⃣ В САМЫЙ КОНЕЦ Fallback
        from core.handlers.fallback import FallbackHandler
        fallback_handler = FallbackHandler()
        self.dp.include_router(fallback_handler.get_router())
        self.logger.info("FallbackRouter was loaded")

        # Polling
        self.logger.info(f"Bot {self.version_manager.title} v{self.version_manager.version} started successfull")
        await self.dp.start_polling(self.bot)

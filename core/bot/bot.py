from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from core.config import ConfigManager
from core.plugins import PluginManager
from core.middlewares import UserInitMiddleware
from core.handlers import callbacks, errors
from core.handlers.start import StartHandler
from core.display import ImageManager
from core.handlers import fallback
from databases import DatabaseManager
from .logging import start_logging, logger
import plugins as loaded_plugins


class BotApp:
    """
    Основной класс бота с исправленными зависимостями
    """

    def __init__(self):
        # 0️⃣ Логирование
        start_logging()

        # 1️⃣ Конфигурация
        self.config = ConfigManager()
        logger.info("ConfigManager was loaded")

        # 2️⃣ База данных
        self.db = DatabaseManager(self.config.settings.DATABASE_URL)
        logger.info("DatabaseManager was loaded")

        # 3️⃣ Изображения
        self.images = ImageManager(use_local=True)
        logger.info("ImageManager was loaded")

        # 4️⃣ Плагины
        self.plugin_manager = PluginManager(config_manager=self.config, db=self.db)
        logger.info("PluginManager was loaded")
        self.loaded_plugins = loaded_plugins
        self.plugins = self.plugin_manager.load_all()

        # 5️⃣ Стартовый хендлер
        self.start_handler = StartHandler(
            db=self.db,
            images=self.images,
            plugins=self.plugins,
            config=self.config
        )
        logger.info("StartHandler was loaded")

        # 6️⃣ Бот и диспетчер
        self.bot = Bot(token=self.config.settings.BOT_TOKEN,
                       default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.dp = Dispatcher(storage=MemoryStorage())

    async def run(self):
        """
        Запускает бота с исправленными зависимостями
        """
        # Инициализация базы
        await self.db.init()
        logger.info("Database was initialized")

        # Middleware
        self.dp.message.middleware(UserInitMiddleware())
        logger.info("Middlewares was loaded")

        # Роутеры плагинов
        for plugin in self.plugins.values():
            self.dp.include_router(plugin.get_router())
        logger.info("PluginRouters was loaded")

        # Роутеры ядра
        self.start_handler.register(self.dp)
        self.dp.include_router(callbacks.router)
        self.dp.include_router(errors.router)
        logger.info("CoreRouters was loaded")

        # Fallback
        self.dp.include_router(fallback.router)
        logger.info("FallbackRouter was loaded")

        # Polling
        logger.info("Bot starting...")
        await self.dp.start_polling(self.bot)

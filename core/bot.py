from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from core.config import ConfigManager
from core.plugins import PluginManager
from core.middlewares import UserInitMiddleware
from core.handlers.start import StartHandler
from core.display import ImageManager
from modules.databases import DatabaseManager
from core.logging import LoggingManager
from core.version import VersionManager
from core.auth import AuthManager
from core.stats import StatsManager


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

        # 4️⃣ Бот и диспетчер
        self.bot = Bot(token=self.config.settings.BOT_TOKEN,
                       default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.dp = Dispatcher(storage=MemoryStorage())

        # 5️⃣ PluginManager
        self.plugin_manager = PluginManager(config_manager=self.config, db=self.db, dp=self.dp)
        self.logger.info("PluginManager was loaded")

        # Сохраняем PluginManager в конфиг для доступа плагинами
        self.config.set_plugin_manager(self.plugin_manager)

        self.plugins = self.plugin_manager.load_all()

        # 6️⃣ Стартовый хендлер
        self.start_handler = StartHandler(
            images=self.images,
            plugins=self.plugins,
            config=self.config
        )
        self.logger.info("StartHandler was loaded")

        # 7️⃣ Менеджер аутентификации (объединяем Auth и RBAC)
        self.auth_manager = AuthManager(self.config)
        self.logger.info("AuthManager was loaded")

        # 8️⃣ RBAC инициализируется внутри AuthManager
        self.logger.info("RBACManager was loaded")

        # 9️⃣ Менеджер статистики
        self.stats_manager = StatsManager(self.config, self.db, self.plugin_manager)
        self.logger.info("StatsManager was loaded")

        # 🔟 Менеджер версий
        self.version_manager = VersionManager()

    async def run(self):
        """
        Запускает бота с правильным порядком загрузки роутеров
        """
        # Инициализация базы
        await self.db.init()
        self.logger.info("Database was initialized")

        try:
            await self.auth_manager.rbac.initialize_system()
            self.logger.info("RBAC system initialized")

            # ДОБАВЛЯЕМ ОТЛАДКУ
            await self.auth_manager.rbac.debug_rbac_state()

        except Exception as e:
            self.logger.error(f"RBAC initialization failed: {e}")

        # Middleware
        self.dp.message.middleware(UserInitMiddleware())
        self.logger.info("Middlewares was initialized")

        # 1️⃣ Сначала роутеры ЯДРА (важно!)
        self.dp.include_router(self.start_handler.get_router())

        # ErrorHandler
        from core.handlers.errors import ErrorHandler
        error_handler = ErrorHandler()
        self.dp.include_router(error_handler.get_router())
        self.logger.info("CoreRouters was initialized")

        # 2️⃣ Затем роутеры ПЛАГИНОВ
        for plugin in self.plugins.values():
            self.dp.include_router(plugin.get_router())
        self.logger.info("PluginRouters was initialized")

        # 3️⃣ В САМЫЙ КОНЕЦ Fallback
        from core.handlers.fallback import FallbackHandler
        fallback_handler = FallbackHandler()
        self.dp.include_router(fallback_handler.get_router())
        self.logger.info("FallbackRouter was initialized")

        # Polling
        self.logger.info(f"Bot {self.version_manager.title} v{self.version_manager.version} started successfull")
        await self.dp.start_polling(self.bot)

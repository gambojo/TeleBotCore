from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from core.config import ConfigManager

Base = declarative_base()


class DatabaseManager:
    """
    Менеджер для работы с базой данных
    """

    def __init__(self, db_url: str = None):
        if db_url is None:
            config = ConfigManager()
            db_url = config.settings.DATABASE_URL

        self.engine = create_async_engine(db_url, echo=False)
        self.async_session_maker = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def init(self):
        """
        Инициализирует БД, создавая все таблицы
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def create_session(self) -> AsyncSession:
        """
        Создает новую сессию БД
        Возвращает: AsyncSession - асинхронная сессия SQLAlchemy
        Пример: session = db.create_session()
        """
        return self.async_session_maker()

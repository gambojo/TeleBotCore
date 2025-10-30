from pydantic_settings import BaseSettings, SettingsConfigDict


class CoreSettings(BaseSettings):
    """
    Базовые настройки приложения, загружаемые из .env файла
    Параметры: наследует от BaseSettings
    Возвращает: экземпляр с загруженными настройками
    Пример: settings = CoreSettings()
    """

    BOT_TOKEN: str
    ADMIN_IDS: str
    DATABASE_URL: str = "sqlite+aiosqlite:///db.sqlite3"
    SUPPORT: str = "support"
    PLUGINS_DISPLAY_MODE: str = "integrated"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

    @property
    def admin_ids(self) -> list[int]:
        """
        Преобразует строку ADMIN_IDS в список чисел
        Возвращает: list[int] - список ID администраторов
        Пример: settings.admin_ids -> [123456, 789012]
        """
        return [int(x) for x in self.ADMIN_IDS.strip("[]").split(",") if x]

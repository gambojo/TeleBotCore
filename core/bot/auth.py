from core.config import ConfigManager

config = ConfigManager()

def determine_role(telegram_id: int) -> str:
    """
    Определяет роль пользователя по его Telegram ID
    Параметры: telegram_id - идентификатор пользователя в Telegram
    Возвращает: str - 'admin' или 'user'
    Пример: determine_role(123456) -> 'admin'
    """
    if telegram_id in config.settings.admin_ids:
        return "admin"
    return "user"

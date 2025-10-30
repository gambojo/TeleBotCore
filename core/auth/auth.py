from core.config import ConfigManager


class AuthManager:
    """
    Менеджер аутентификации и авторизации пользователей
    Параметры: config_manager - менеджер конфигурации (опционально)
    Возвращает: экземпляр AuthManager
    Пример: auth = AuthManager()
    """

    def __init__(self, config_manager: ConfigManager = None):
        self.config = config_manager or ConfigManager()

    def determine_role(self, telegram_id: int) -> str:
        """
        Определяет роль пользователя по его Telegram ID
        Параметры: telegram_id - идентификатор пользователя в Telegram
        Возвращает: str - 'admin' или 'user'
        Пример: auth.determine_role(123456) -> 'admin'
        """
        if telegram_id in self.config.settings.admin_ids:
            return "admin"
        return "user"

    def is_admin(self, telegram_id: int) -> bool:
        """
        Проверяет является ли пользователь администратором
        Параметры: telegram_id - идентификатор пользователя в Telegram
        Возвращает: bool - True если администратор
        Пример: auth.is_admin(123456) -> True
        """
        return self.determine_role(telegram_id) == "admin"

    def get_admin_ids(self) -> list[int]:
        """
        Возвращает список ID администраторов
        Возвращает: list[int] - список ID администраторов
        Пример: auth.get_admin_ids() -> [123456, 789012]
        """
        return self.config.settings.admin_ids


# Для обратной совместимости со старым кодом
_auth_manager = AuthManager()
determine_role = _auth_manager.determine_role

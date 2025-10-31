class DatabaseError(Exception):
    """Базовое исключение для ошибок базы данных"""
    pass


class UserNotFoundError(DatabaseError):
    """Пользователь не найден"""
    pass


class UserAlreadyExistsError(DatabaseError):
    """Пользователь уже существует"""
    pass


class DatabaseConnectionError(DatabaseError):
    """Ошибка подключения к базе данных"""
    pass


class DatabaseIntegrityError(DatabaseError):
    """Ошибка целостности данных"""
    pass

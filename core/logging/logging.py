import logging
from typing import Dict, Any, Optional


class PluginLoggerAdapter(logging.LoggerAdapter):
    """
    Адаптер для логирования с контекстом плагина
    Параметры: базовый логгер и дополнительный контекст
    Возвращает: адаптированное сообщение для логирования
    Пример: logger = PluginLoggerAdapter(base_logger, {'plugin': 'VPN'})
    """

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        context = " | ".join(f"{k}={v}" for k, v in self.extra.items())
        return f"[{context}] {msg}", kwargs


class LoggingManager:
    """
    Менеджер для управления логированием во всем приложении
    Параметры: config - конфигурация логирования (опционально)
    Возвращает: экземпляр LoggingManager
    Пример: log_manager = LoggingManager()
    """

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, level: int = logging.INFO,
                 format_str: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"):
        if not self._initialized:
            self.level = level
            self.format_str = format_str
            self._plugin_loggers: Dict[str, PluginLoggerAdapter] = {}
            self._setup_logging()
            self._initialized = True

    def _setup_logging(self) -> None:
        """
        Инициализирует базовую конфигурацию логирования
        """
        logging.basicConfig(
            level=self.level,
            format=self.format_str,
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        self.get_logger(__name__).info("Logging system initialized")

    def get_logger(self, name: str) -> logging.Logger:
        """
        Возвращает стандартный логгер
        Параметры: name - имя логгера
        Возвращает: logging.Logger
        Пример: logger = log_manager.get_logger(__name__)
        """
        return logging.getLogger(name)

    def get_plugin_logger(self, plugin_name: str, **extra_context) -> PluginLoggerAdapter:
        """
        Создает или возвращает логгер для плагина с контекстом
        Параметры: plugin_name - имя плагина, extra_context - дополнительный контекст
        Возвращает: PluginLoggerAdapter
        Пример: logger = log_manager.get_plugin_logger('VPN', user_id=123)
        """
        if plugin_name not in self._plugin_loggers:
            base_logger = logging.getLogger(plugin_name)
            context = {"plugin": plugin_name, **extra_context}
            self._plugin_loggers[plugin_name] = PluginLoggerAdapter(base_logger, context)

        return self._plugin_loggers[plugin_name]

    def set_level(self, level: int) -> None:
        """
        Устанавливает уровень логирования для всех логгеров
        Параметры: level - уровень логирования (logging.DEBUG, INFO, etc.)
        """
        logging.getLogger().setLevel(level)
        self.level = level

    def add_file_handler(self, filename: str, level: Optional[int] = None) -> None:
        """
        Добавляет файловый обработчик для логирования
        Параметры: filename - имя файла, level - уровень (опционально)
        """
        file_handler = logging.FileHandler(filename, encoding='utf-8')
        formatter = logging.Formatter(self.format_str)
        file_handler.setFormatter(formatter)

        if level:
            file_handler.setLevel(level)

        logging.getLogger().addHandler(file_handler)

    def get_logging_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию о текущей конфигурации логирования
        Возвращает: dict с информацией о логировании
        """
        return {
            "level": logging.getLevelName(self.level),
            "format": self.format_str,
            "active_plugin_loggers": list(self._plugin_loggers.keys())
        }

import logging


class PluginLoggerAdapter(logging.LoggerAdapter):
    """
    Адаптер для логирования с контекстом плагина
    Параметры: базовый логгер и дополнительный контекст
    Возвращает: адаптированное сообщение для логирования
    Пример: logger = PluginLoggerAdapter(base_logger, {'plugin': 'VPN'})
    """

    def process(self, msg, kwargs):
        context = " | ".join(f"{k}={v}" for k, v in self.extra.items())
        return f"[{context}] {msg}", kwargs


def get_plugin_logger(plugin_name: str, **extra_context) -> PluginLoggerAdapter:
    """
    Создает логгер для плагина с контекстом
    Параметры: plugin_name - имя плагина, extra_context - дополнительный контекст
    Возвращает: PluginLoggerAdapter
    Пример: logger = get_plugin_logger('VPN', user_id=123)
    """
    _logger = logging.getLogger(plugin_name)
    context = {"plugin": plugin_name, **extra_context}
    return PluginLoggerAdapter(_logger, context)


def start_logging():
    """
    Инициализирует базовую конфигурацию логирования
    Параметры: не принимает параметров
    Возвращает: None
    Пример: start_logging()
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )


logger = logging.getLogger(__name__)

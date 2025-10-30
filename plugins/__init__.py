import importlib
import pkgutil
import os

_loaded_plugins = []

def auto_import_plugins():
    """
    Автоматически импортирует все плагины из папки plugins
    Возвращает: None
    Пример: вызывается автоматически при импорте модуля
    """
    plugins_dir = os.path.dirname(__file__)

    for _, plugin_name, is_pkg in pkgutil.iter_modules([plugins_dir]):
        if is_pkg and not plugin_name.startswith('_'):
            try:
                importlib.import_module(f'plugins.{plugin_name}')
                _loaded_plugins.append((plugin_name, True, None))
            except ImportError as e:
                _loaded_plugins.append((plugin_name, False, str(e)))

auto_import_plugins()

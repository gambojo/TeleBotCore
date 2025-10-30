from abc import ABC, abstractmethod
import os
import inspect
from aiogram import Router
from aiogram.types import InlineKeyboardButton
from pydantic_settings import BaseSettings
from core.config import ConfigManager
from databases import DatabaseManager

class PluginBase(ABC):
    """
    Базовый абстрактный класс для всех плагинов
    Параметры: config - менеджер конфигурации, db - менеджер БД
    Возвращает: экземпляр плагина
    Пример: class MyPlugin(PluginBase): ...
    """

    @abstractmethod
    def __init__(self, config: ConfigManager, db: DatabaseManager):
        pass

    @abstractmethod
    def get_router(self) -> Router:
        """Возвращает роутер плагина с обработчиками"""
        pass

    @abstractmethod
    def get_integrated_buttons(self) -> list[list[InlineKeyboardButton]]:
        """Возвращает кнопки для интеграции в главное меню"""
        pass

    @abstractmethod
    def get_entry_button(self) -> list[list[InlineKeyboardButton]]:
        """Возвращает кнопку входа в плагин"""
        pass

    @abstractmethod
    def get_config(self) -> type[BaseSettings]:
        """Возвращает класс конфигурации плагина"""
        pass

    @abstractmethod
    def get_settings(self) -> BaseSettings:
        """Возвращает настройки плагина"""
        pass

    def get_name(self) -> str:
        """Возвращает: str - имя плагина в верхнем регистре"""
        # Получаем путь к файлу класса плагина
        plugin_file = inspect.getfile(self.__class__)
        # Получаем имя родительской директории (папки плагина)
        plugin_dir = os.path.basename(os.path.dirname(plugin_file))
        return plugin_dir.upper()

    def get_menu_buttons(self) -> list[list[InlineKeyboardButton]]:
        """Совместимость со старым интерфейсом"""
        return self.get_integrated_buttons()

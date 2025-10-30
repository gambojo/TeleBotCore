from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.plugins.base import PluginBase
from core.config.base_config import CoreSettings
from core.config import ConfigManager
from .keyboard_builder_base import KeyboardBuilderBase


class MainMenuKeyboard(KeyboardBuilderBase):
    """
    Клавиатура главного меню с плагинами
    Параметры: plugins - словарь плагинов, config - конфигурация
    Возвращает: экземпляр MainMenuKeyboard
    Пример: keyboard = MainMenuKeyboard(plugins, config)
    """

    def __init__(self, plugins: dict[str, PluginBase], config: ConfigManager):
        super().__init__()
        self.plugins = plugins
        self.config = config
        self.support_username = config.settings.SUPPORT

    def add_plugin_buttons(self) -> "MainMenuKeyboard":
        """Добавляет кнопки плагинов в зависимости от режима отображения"""
        display_mode = self.config.settings.PLUGINS_DISPLAY_MODE

        for name, plugin in self.plugins.items():
            if display_mode == "integrated":
                buttons = plugin.get_integrated_buttons()
            elif display_mode == "entry":
                buttons = plugin.get_entry_button()
            elif display_mode == "smart":
                buttons = self._get_smart_buttons(plugin)
            else:
                buttons = plugin.get_integrated_buttons()

            if buttons:
                self.keyboard.extend(buttons)
        return self

    def build_markup(self) -> InlineKeyboardMarkup:
        self.keyboard = []
        self.add_plugin_buttons()
        self.add_core_buttons(support_username=self.support_username, enabled=True)
        return InlineKeyboardMarkup(inline_keyboard=self.keyboard)

    def _get_smart_buttons(self, plugin: PluginBase) -> list[list[InlineKeyboardButton]]:
        """Умное отображение плагинов в зависимости от количества кнопок"""
        integrated_buttons = plugin.get_integrated_buttons()
        if len(integrated_buttons) <= 2:
            return integrated_buttons
        return plugin.get_entry_button()

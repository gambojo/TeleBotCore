from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from core.config.base_config import CoreSettings


class KeyboardBuilderBase:
    """
    Базовый класс для построителей клавиатур
    Параметры: не принимает параметров при создании
    Возвращает: экземпляр KeyboardBuilderBase
    Пример: builder = KeyboardBuilderBase()
    """

    def __init__(self):
        self.keyboard: list[list[InlineKeyboardButton]] = []

    def add_button(self, text: str, callback_data: str, url: str = None) -> "KeyboardBuilderBase":
        """
        Удобное декларативное добавление кнопки
        """
        button = InlineKeyboardButton(text=text, callback_data=callback_data) if not url else InlineKeyboardButton(
            text=text, url=url)
        self.keyboard.append([button])
        return self

    def add_row(self, buttons: list[InlineKeyboardButton]) -> "KeyboardBuilderBase":
        """
        Удобное императивное добавление кнопки
        """
        self.keyboard.append(buttons)
        return self

    def add_core_buttons(self, support_username: str = CoreSettings().SUPPORT, position: str = "bottom",
                         enabled: bool = True) -> "KeyboardBuilderBase":
        """
        Добавление кнопок-констант в начало или в конец
        """
        if not enabled:
            return self

        profile_button = [InlineKeyboardButton(text="Профиль", callback_data="core:main_menu")]
        support_button = [InlineKeyboardButton(text="Поддержка", url=f"https://t.me/{support_username}")]

        if position == "top":
            self.keyboard.insert(0, support_button)
            self.keyboard.insert(0, profile_button)
        else:
            self.keyboard.append(profile_button)
            self.keyboard.append(support_button)

        return self

    def build_markup(self) -> InlineKeyboardMarkup:
        """
        Собирает клавиатуру из добавленных кнопок
        Возвращает: InlineKeyboardMarkup - готовая клавиатура
        Пример: keyboard = builder.add_button("Кнопка", "data").build_markup()
        """
        return InlineKeyboardMarkup(inline_keyboard=self.keyboard)

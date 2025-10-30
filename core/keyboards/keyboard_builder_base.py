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
        button = InlineKeyboardButton(text=text, callback_data=callback_data) if not url else InlineKeyboardButton(
            text=text, url=url)
        self.keyboard.append([button])
        return self

    def add_row(self, buttons: list[InlineKeyboardButton]) -> "KeyboardBuilderBase":
        self.keyboard.append(buttons)
        return self

    def add_back(self, callback_data: str = "main") -> "KeyboardBuilderBase":
        self.keyboard.append([
            InlineKeyboardButton(text="Назад", callback_data=callback_data)
        ])
        return self

    def add_cancel(self, callback_data: str = "cancel") -> "KeyboardBuilderBase":
        self.keyboard.append([
            InlineKeyboardButton(text="Отмена", callback_data=callback_data)
        ])
        return self

    def add_navigation(self, back: str = "main", cancel: str = "cancel") -> "KeyboardBuilderBase":
        self.keyboard.append([
            InlineKeyboardButton(text="Назад", callback_data=back),
            InlineKeyboardButton(text="Отмена", callback_data=cancel)
        ])
        return self

    def add_core_buttons(self, support_username: str = CoreSettings().SUPPORT, position: str = "bottom",
                         enabled: bool = True) -> "KeyboardBuilderBase":
        if not enabled:
            return self

        profile_button = [InlineKeyboardButton(text="Профиль", callback_data="main")]
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

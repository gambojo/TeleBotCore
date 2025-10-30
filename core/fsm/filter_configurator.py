from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from core.keyboards import KeyboardBuilderBase
from core.display.html_builder import HTMLBuilder
from .registry import FilterFSM


class FilterConfigurator:
    """
    Конфигуратор фильтров через FSM
    Параметры: router - роутер для регистрации обработчиков
    Возвращает: экземпляр FilterConfigurator
    Пример: configurator = FilterConfigurator(router)
    """

    def __init__(self, router: Router):
        self.router = router
        self._register_handlers()

    def _register_handlers(self):
        """Регистрирует обработчики для конфигурации фильтров"""
        self.router.message.register(self.start_filter_config, Command("configure_filters"))
        self.router.callback_query.register(self.handle_role_filter_setup, F.data == "configure_role_filter")
        self.router.message.register(self.handle_role_input, FilterFSM.awaiting_role_input)
        self.router.callback_query.register(self.cancel_configuration, F.data == "cancel_filter_config")

    async def start_filter_config(self, message: Message, state: FSMContext):
        """Начинает процесс конфигурации фильтров"""
        text = HTMLBuilder().title("Конфигурация фильтров", "⚙️").build()

        keyboard = (KeyboardBuilderBase()
                    .add_button("Настроить RoleFilter", "configure_role_filter")
                    .add_button("Настроить PermissionFilter", "configure_permission_filter")
                    .add_button("Настроить GroupFilter", "configure_group_filter")
                    .add_cancel())

        await message.answer(text, reply_markup=keyboard.build_markup())
        await state.set_state(FilterFSM.configuring_role_filter)

    async def handle_role_filter_setup(self, callback: CallbackQuery, state: FSMContext):
        """Обрабатывает настройку RoleFilter"""
        text = HTMLBuilder().title("Настройка RoleFilter", "👥").note(
            "Введите требуемую роль (например: admin, user, moderator)").build()

        keyboard = KeyboardBuilderBase().add_cancel()

        await callback.message.edit_text(text, reply_markup=keyboard.build_markup())
        await state.set_state(FilterFSM.awaiting_role_input)

    async def handle_role_input(self, message: Message, state: FSMContext):
        """Обрабатывает ввод роли для RoleFilter"""
        role = message.text.strip()
        await state.update_data(configured_role=role)
        text = (HTMLBuilder()
                .title("RoleFilter настроен", "✅")
                .field("Роль", role)
                .note("Используйте в коде: RoleFilter(user_manager, 'ваша_роль')")
                .build())

        await message.answer(text)
        await state.clear()

    async def cancel_configuration(self, callback: CallbackQuery, state: FSMContext):
        """Отменяет конфигурацию фильтров"""
        await state.clear()
        await callback.message.edit_text("❌ Конфигурация фильтров отменена")

from aiogram.fsm.state import State, StatesGroup


class ConfirmFSM(StatesGroup):
    """Состояния для подтверждения действий"""
    waiting = State()
    confirmed = State()
    cancelled = State()


class UserFSM(StatesGroup):
    """Состояния для сбора пользовательских данных"""
    awaiting_email = State()
    awaiting_phone = State()
    awaiting_name = State()


class AdminFSM(StatesGroup):
    """Состояния для административных действий"""
    awaiting_broadcast_text = State()
    awaiting_role_assignment = State()


class PluginFSM(StatesGroup):
    """Состояния для конфигурации плагинов"""
    configuring = State()
    testing = State()
    awaiting_settings = State()


class FilterFSM(StatesGroup):
    """Состояния для настройки фильтров"""
    configuring_role_filter = State()
    configuring_permission_filter = State()
    configuring_group_filter = State()
    awaiting_role_input = State()
    awaiting_permission_flags = State()
    awaiting_chat_ids = State()

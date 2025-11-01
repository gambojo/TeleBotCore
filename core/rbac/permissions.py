from dataclasses import dataclass


@dataclass(frozen=True)
class Permission:
    """Базовый класс для разрешений"""
    name: str
    description: str
    category: str


class SystemPermissions:
    """Системные разрешения"""
    # Управление пользователями
    USER_VIEW = Permission("user.view", "Просмотр пользователей", "user_management")
    USER_EDIT = Permission("user.edit", "Редактирование пользователей", "user_management")
    USER_DELETE = Permission("user.delete", "Удаление пользователей", "user_management")
    USER_ROLE_ASSIGN = Permission("user.role.assign", "Назначение ролей", "user_management")

    # Управление плагинами
    PLUGIN_VIEW = Permission("plugin.view", "Просмотр плагинов", "plugin_management")
    PLUGIN_INSTALL = Permission("plugin.install", "Установка плагинов", "plugin_management")
    PLUGIN_CONFIGURE = Permission("plugin.configure", "Настройка плагинов", "plugin_management")
    PLUGIN_UNINSTALL = Permission("plugin.uninstall", "Удаление плагинов", "plugin_management")

    # Системные
    SYSTEM_STATS_VIEW = Permission("system.stats.view", "Просмотр статистики", "system")
    SYSTEM_LOGS_VIEW = Permission("system.logs.view", "Просмотр логов", "system")
    SYSTEM_SETTINGS_EDIT = Permission("system.settings.edit", "Редактирование настроек", "system")

    # Админ-панель
    ADMIN_PANEL_ACCESS = Permission("admin_panel.access", "Доступ к админ-панели", "admin_panel")
    ADMIN_PANEL_DASHBOARD = Permission("admin_panel.dashboard", "Просмотр дашборда", "admin_panel")

    @classmethod
    def get_all_permissions(cls):
        """Возвращает все системные разрешения"""
        return {value for key, value in cls.__dict__.items()
                if isinstance(value, Permission)}



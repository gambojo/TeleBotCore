from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from modules.databases import DatabaseManager
from modules.databases.models import User
from .models import RBACRole, RBACPermission, user_roles, role_permissions
from core.logging import LoggingManager
from .permissions import SystemPermissions
from functools import lru_cache
from core.config import ConfigManager


class RBACManager:
    """
    Упрощенный RBAC менеджер без сложных отношений
    """

    @lru_cache(maxsize=1000)
    async def user_has_permission_cached(self, user_id: int, permission: str) -> bool:
        return await self.user_has_permission(user_id, permission)

    def __init__(self, db: DatabaseManager, config: ConfigManager = None):
        self.db = db
        self.config = config or ConfigManager()
        self.logger = LoggingManager().get_logger(__name__)

    async def _get_session(self) -> AsyncSession:
        return self.db.create_session()

    async def initialize_system(self):
        """Инициализация RBAC системы"""
        if not self.config.settings.RBAC_ENABLED:
            self.logger.info("RBAC system is disabled via config")
            return

        await self.initialize_default_roles()
        await self.sync_legacy_admins()

    async def initialize_default_roles(self):
        """Инициализирует стандартные роли и разрешения - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        session = await self._get_session()
        try:
            async with session:
                # Сначала создаем все разрешения
                permissions_map = {}
                for permission in SystemPermissions.get_all_permissions():
                    # Проверяем существование разрешения
                    result = await session.execute(
                        select(RBACPermission).where(RBACPermission.name == permission.name)
                    )
                    existing_perm = result.scalar_one_or_none()

                    if not existing_perm:
                        new_perm = RBACPermission(
                            name=permission.name,
                            description=permission.description,
                            category=permission.category
                        )
                        session.add(new_perm)
                        await session.flush()  # Получаем ID
                        permissions_map[permission.name] = new_perm
                        self.logger.info(f"Created permission: {permission.name}")
                    else:
                        permissions_map[permission.name] = existing_perm
                        self.logger.info(f"Permission already exists: {permission.name}")

                await session.commit()
                self.logger.info(f"Created {len(permissions_map)} permissions")

                # ИСПРАВЛЕННЫЙ конфиг ролей - super_admin должен иметь ВСЕ разрешения
                roles_config = {
                    "super_admin": {
                        "description": "Супер администратор - полный доступ",
                        "permissions": [perm.name for perm in SystemPermissions.get_all_permissions()],
                        # ← ВСЕ разрешения
                    },
                    "admin": {
                        "description": "Администратор - основные функции",
                        "permissions": [
                            perm.name for perm in SystemPermissions.get_all_permissions()
                            if not perm.name.startswith("system.")
                        ],
                    },
                    "user": {
                        "description": "Обычный пользователь",
                        "permissions": [],
                    }
                }

                self.logger.info(f"Role config - super_admin permissions: {roles_config['super_admin']['permissions']}")

                for role_name, config in roles_config.items():
                    # Проверяем существование роли
                    result = await session.execute(
                        select(RBACRole).where(RBACRole.name == role_name)
                    )
                    existing_role = result.scalar_one_or_none()

                    if not existing_role:
                        new_role = RBACRole(
                            name=role_name,
                            description=config["description"],
                            is_default=(role_name == "user")
                        )
                        session.add(new_role)
                        await session.flush()  # Получаем ID роли
                        self.logger.info(f"Created role: {role_name} (ID: {new_role.id})")

                        # Назначаем разрешения через прямую вставку в таблицу
                        permission_count = 0
                        for perm_name in config["permissions"]:
                            if perm_name in permissions_map:
                                await session.execute(
                                    insert(role_permissions).values(
                                        role_id=new_role.id,
                                        permission_id=permissions_map[perm_name].id
                                    )
                                )
                                permission_count += 1
                                self.logger.info(f"  - Assigned permission: {perm_name} to {role_name}")

                        self.logger.info(f"Assigned {permission_count} permissions to {role_name}")

                    else:
                        self.logger.info(f"Role already exists: {role_name} (ID: {existing_role.id})")

                        # УДАЛЯЕМ старые разрешения и назначаем новые
                        await session.execute(
                            delete(role_permissions).where(role_permissions.c.role_id == existing_role.id)
                        )

                        # Назначаем новые разрешения
                        permission_count = 0
                        for perm_name in config["permissions"]:
                            if perm_name in permissions_map:
                                await session.execute(
                                    insert(role_permissions).values(
                                        role_id=existing_role.id,
                                        permission_id=permissions_map[perm_name].id
                                    )
                                )
                                permission_count += 1
                                self.logger.info(f"  - Re-assigned permission: {perm_name} to {role_name}")

                        self.logger.info(f"Re-assigned {permission_count} permissions to {role_name}")

                await session.commit()
                self.logger.info("Default RBAC roles and permissions initialized")

        except Exception as e:
            await session.rollback()
            self.logger.error(f"Error initializing default roles: {e}")
            raise

    async def user_has_permission(self, user_id: int, permission: str) -> bool:
        """Проверяет разрешение через несколько простых запросов с отладкой"""
        self.logger.info(f"🔐 Checking permission '{permission}' for user {user_id}")

        session = await self._get_session()
        try:
            async with session:
                # Находим пользователя
                user_result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()

                if not user:
                    self.logger.warning(f"User {user_id} not found in database")
                    return False

                self.logger.info(f"User found: ID={user.id}, Telegram ID={user.telegram_id}")

                # Находим роли пользователя
                user_roles_result = await session.execute(
                    select(user_roles.c.role_id)
                    .where(user_roles.c.user_id == user.id)
                )
                role_ids = [row[0] for row in user_roles_result.all()]

                self.logger.info(f"User {user_id} has role IDs: {role_ids}")

                if not role_ids:
                    self.logger.warning(f"User {user_id} has no roles assigned")
                    return False

                # Находим названия ролей для отладки
                roles_result = await session.execute(
                    select(RBACRole.name)
                    .where(RBACRole.id.in_(role_ids))
                )
                role_names = [row[0] for row in roles_result.all()]
                self.logger.info(f"User {user_id} has roles: {role_names}")

                # Находим разрешения для этих ролей
                role_perms_result = await session.execute(
                    select(role_permissions.c.permission_id)
                    .where(role_permissions.c.role_id.in_(role_ids))
                )
                permission_ids = [row[0] for row in role_perms_result.all()]

                self.logger.info(f"User {user_id} has permission IDs: {permission_ids}")

                if not permission_ids:
                    self.logger.warning(f"User {user_id} has no permissions")
                    return False

                # Находим названия разрешений для отладки
                perms_result = await session.execute(
                    select(RBACPermission.name)
                    .where(RBACPermission.id.in_(permission_ids))
                )
                perm_names = [row[0] for row in perms_result.all()]
                self.logger.info(f"User {user_id} has permissions: {perm_names}")

                # Проверяем наличие нужного разрешения
                perm_result = await session.execute(
                    select(RBACPermission.id)
                    .where(
                        RBACPermission.id.in_(permission_ids),
                        RBACPermission.name == permission
                    )
                    .limit(1)
                )

                has_perm = perm_result.first() is not None
                self.logger.info(f"User {user_id} has permission '{permission}': {has_perm}")
                return has_perm

        except Exception as e:
            self.logger.error(f"Error checking permission: {e}")
            return False

    async def get_user_roles(self, user_id: int) -> List[str]:
        """Возвращает роли пользователя через прямой запрос"""
        if not self.config.settings.RBAC_ENABLED:
            return [self.config.settings.DEFAULT_ROLE]

        session = await self._get_session()
        try:
            async with session:
                # Находим пользователя
                user_result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()

                if not user:
                    return ["user"]

                # Прямой запрос для получения ролей
                result = await session.execute(
                    select(RBACRole.name)
                    .select_from(user_roles.join(RBACRole))
                    .where(user_roles.c.user_id == user.id)
                )

                roles = result.scalars().all()
                return list(roles) if roles else ["user"]

        except Exception as e:
            self.logger.error(f"Error getting user roles: {e}")
            return ["user"]

    async def assign_role_to_user(self, user_id: int, role_name: str) -> bool:
        """Назначает роль через прямую работу с таблицами"""
        session = await self._get_session()
        try:
            async with session:
                # Находим пользователя
                user_result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()

                if not user:
                    self.logger.warning(f"User {user_id} not found")
                    return False

                # Находим роль
                role_result = await session.execute(
                    select(RBACRole).where(RBACRole.name == role_name)
                )
                role = role_result.scalar_one_or_none()

                if not role:
                    self.logger.warning(f"Role {role_name} not found")
                    return False

                # Проверяем существующую связь
                existing_result = await session.execute(
                    select(user_roles).where(
                        user_roles.c.user_id == user.id,
                        user_roles.c.role_id == role.id
                    )
                )

                if existing_result.first():
                    self.logger.debug(f"User already has role {role_name}")
                    return True

                # Создаем связь
                await session.execute(
                    insert(user_roles).values(user_id=user.id, role_id=role.id)
                )
                await session.commit()

                self.logger.info(f"Assigned role {role_name} to user {user_id}")
                return True

        except Exception as e:
            await session.rollback()
            self.logger.error(f"Error assigning role: {e}")
            return False

    async def remove_user_role(self, user_id: int, role_name: str) -> bool:
        """Удаляет роль через прямую работу с таблицами"""
        session = await self._get_session()
        try:
            async with session:
                # Находим пользователя
                user_result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()

                if not user:
                    self.logger.warning(f"User {user_id} not found")
                    return False

                # Находим роль
                role_result = await session.execute(
                    select(RBACRole).where(RBACRole.name == role_name)
                )
                role = role_result.scalar_one_or_none()

                if not role:
                    self.logger.warning(f"Role {role_name} not found")
                    return False

                # Удаляем связь
                result = await session.execute(
                    delete(user_roles).where(
                        user_roles.c.user_id == user.id,
                        user_roles.c.role_id == role.id
                    )
                )

                if result.rowcount > 0:
                    await session.commit()
                    self.logger.info(f"Removed role {role_name} from user {user_id}")
                    return True
                else:
                    self.logger.debug(f"User didn't have role {role_name}")
                    return True

        except Exception as e:
            await session.rollback()
            self.logger.error(f"Error removing role: {e}")
            return False

    async def get_users_with_role(self, role_name: str) -> List[int]:
        """Возвращает пользователей с ролью через прямой запрос"""
        session = await self._get_session()
        try:
            async with session:
                result = await session.execute(
                    select(User.telegram_id)
                    .select_from(user_roles.join(User))
                    .join(RBACRole)
                    .where(RBACRole.name == role_name)
                )
                return list(result.scalars().all())

        except Exception as e:
            self.logger.error(f"Error getting users with role: {e}")
            return []

    async def sync_legacy_admins(self):
        """Синхронизирует администраторов из config с подробным логированием"""
        try:
            from core.config import ConfigManager
            config = ConfigManager()

            self.logger.info(f"🔄 Starting legacy admin sync. ADMIN_IDS: {config.settings.admin_ids}")

            synced_count = 0
            for admin_id in config.settings.admin_ids:
                self.logger.info(f"Processing admin ID: {admin_id}")

                # Проверяем текущие роли пользователя
                current_roles = await self.get_user_roles(admin_id)
                self.logger.info(f"User {admin_id} current roles: {current_roles}")

                if "super_admin" not in current_roles:
                    self.logger.info(f"Assigning super_admin role to {admin_id}")
                    success = await self.assign_role_to_user(admin_id, "super_admin")
                    if success:
                        synced_count += 1
                        self.logger.info(f"✅ Successfully assigned super_admin to {admin_id}")
                    else:
                        self.logger.error(f"❌ Failed to assign super_admin to {admin_id}")
                else:
                    self.logger.info(f"User {admin_id} already has super_admin role")

                # Проверяем результат
                final_roles = await self.get_user_roles(admin_id)
                self.logger.info(f"User {admin_id} final roles: {final_roles}")

            self.logger.info(f"🔄 Legacy admin sync completed: {synced_count} admins synced")
            return synced_count

        except Exception as e:
            self.logger.error(f"Error syncing legacy admins: {e}")
            return 0

    async def debug_rbac_state(self):
        """Выводит отладочную информацию о состоянии RBAC"""
        session = await self._get_session()
        try:
            async with session:
                # Проверяем существующие роли
                roles_result = await session.execute(select(RBACRole))
                roles = roles_result.scalars().all()
                self.logger.info("=== RBAC ROLES ===")
                for role in roles:
                    self.logger.info(f"Role: {role.name} (ID: {role.id}) - {role.description}")

                # Проверяем существующие разрешения
                perms_result = await session.execute(select(RBACPermission))
                perms = perms_result.scalars().all()
                self.logger.info("=== RBAC PERMISSIONS ===")
                for perm in perms:
                    self.logger.info(f"Permission: {perm.name} (Category: {perm.category})")

                # Проверяем связи ролей и разрешений
                self.logger.info("=== ROLE-PERMISSION MAPPINGS ===")
                for role in roles:
                    # Получаем разрешения для роли через прямые запросы
                    role_perms_result = await session.execute(
                        select(RBACPermission.name)
                        .select_from(role_permissions)
                        .join(RBACPermission, role_permissions.c.permission_id == RBACPermission.id)
                        .where(role_permissions.c.role_id == role.id)
                    )
                    role_perms = [row[0] for row in role_perms_result.all()]
                    self.logger.info(f"Role '{role.name}' has permissions: {role_perms}")

                # Проверяем пользователей и их роли
                users_result = await session.execute(select(User))
                users = users_result.scalars().all()
                self.logger.info("=== USERS AND THEIR ROLES ===")
                for user in users:
                    user_roles_result = await session.execute(
                        select(RBACRole.name)
                        .select_from(user_roles)
                        .join(RBACRole, user_roles.c.role_id == RBACRole.id)
                        .where(user_roles.c.user_id == user.id)
                    )
                    user_roles_list = [row[0] for row in user_roles_result.all()]
                    self.logger.info(f"User {user.telegram_id} ({user.username}) has roles: {user_roles_list}")

        except Exception as e:
            self.logger.error(f"Error in RBAC debug: {e}")

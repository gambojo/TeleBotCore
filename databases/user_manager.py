from sqlalchemy import select, exc
from sqlalchemy.ext.asyncio import AsyncSession
from core.bot.auth import determine_role
from core.bot.logging import logger
from .models import User
from .database_manager import DatabaseManager
from .exceptions import (
    DatabaseError,
    UserNotFoundError,
    UserAlreadyExistsError,
    DatabaseConnectionError,
    DatabaseIntegrityError
)


class UserManager:
    """
    Менеджер для операций с пользователями в БД с обработкой ошибок
    """

    def __init__(self):
        self.db = DatabaseManager()

    async def _get_session(self) -> AsyncSession:
        # Используем create_session() вместо get_session()
        return self.db.create_session()

    async def _handle_db_error(self, error: Exception, operation: str) -> None:
        """Обрабатывает ошибки базы данных и логирует их"""
        logger.error(f"Database error in {operation}: {error}")

        if isinstance(error, exc.IntegrityError):
            if "unique constraint" in str(error).lower():
                raise UserAlreadyExistsError(f"User already exists: {error}") from error
            raise DatabaseIntegrityError(f"Data integrity error: {error}") from error
        elif isinstance(error, exc.OperationalError):
            raise DatabaseConnectionError(f"Database connection error: {error}") from error
        else:
            raise DatabaseError(f"Database error in {operation}: {error}") from error

    async def get(self, telegram_id: int) -> User | None:
        """
        Получает пользователя по Telegram ID
        """
        session: AsyncSession = await self._get_session()
        try:
            async with session:
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()

                if not user:
                    logger.debug(f"User not found: telegram_id={telegram_id}")

                return user

        except Exception as e:
            await self._handle_db_error(e, "get_user")
            return None

    async def create(self, telegram_id: int, username: str = None, first_name: str = None,
                     last_name: str = None, role: str = "user") -> User:
        """
        Создает нового пользователя
        """
        session: AsyncSession = await self._get_session()
        try:
            async with session:
                is_admin = role == "admin"
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    is_admin=is_admin,
                    role=role
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)

                logger.info(f"User created: telegram_id={telegram_id}, username={username}")
                return user

        except Exception as e:
            await self._handle_db_error(e, "create_user")
            return None

    async def update(self, telegram_id: int, username: str = None, first_name: str = None,
                     last_name: str = None, role: str = None) -> User:
        """
        Обновляет данные пользователя по telegram_id
        """
        session: AsyncSession = await self._get_session()
        try:
            async with session:
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()

                if not user:
                    raise UserNotFoundError(f"User with telegram_id={telegram_id} not found")

                updated = False
                if username is not None and user.username != username:
                    user.username = username
                    updated = True
                if first_name is not None and user.first_name != first_name:
                    user.first_name = first_name
                    updated = True
                if last_name is not None and user.last_name != last_name:
                    user.last_name = last_name
                    updated = True
                if role is not None and user.role != role:
                    user.role = role
                    user.is_admin = role == "admin"
                    updated = True

                if updated:
                    await session.commit()
                    await session.refresh(user)
                    logger.info(f"User updated: telegram_id={telegram_id}")

                return user

        except Exception as e:
            await self._handle_db_error(e, "update_user")
            raise

    async def ensure(self, telegram_id: int, username: str = None, first_name: str = None,
                     last_name: str = None) -> tuple[User, bool]:
        """
        Создает пользователя если не существует, иначе обновляет
        """
        session: AsyncSession = await self._get_session()
        try:
            async with session:
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()

                if user:
                    # Обновляем существующего пользователя
                    updated = False
                    if username is not None and user.username != username:
                        user.username = username
                        updated = True
                    if first_name is not None and user.first_name != first_name:
                        user.first_name = first_name
                        updated = True
                    if last_name is not None and user.last_name != last_name:
                        user.last_name = last_name
                        updated = True

                    # Всегда проверяем роль
                    current_role = determine_role(telegram_id)
                    if user.role != current_role:
                        user.role = current_role
                        user.is_admin = current_role == "admin"
                        updated = True

                    if updated:
                        await session.commit()
                        await session.refresh(user)
                        logger.debug(f"User ensured (updated): telegram_id={telegram_id}")
                    else:
                        logger.debug(f"User ensured (no changes): telegram_id={telegram_id}")

                    return user, False

                # Создаем нового пользователя
                current_role = determine_role(telegram_id)
                new_user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    role=current_role,
                    is_admin=current_role == "admin"
                )
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)

                logger.info(f"User ensured (new): telegram_id={telegram_id}")
                return new_user, True

        except Exception as e:
            await self._handle_db_error(e, "ensure_user")
            raise

    async def delete(self, telegram_id: int) -> bool:
        """
        Удаляет пользователя по Telegram ID
        """
        session: AsyncSession = await self._get_session()
        try:
            async with session:
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()
                if not user:
                    logger.warning(f"User not found for deletion: telegram_id={telegram_id}")
                    return False

                await session.delete(user)
                await session.commit()

                logger.info(f"User deleted: telegram_id={telegram_id}")
                return True

        except Exception as e:
            await self._handle_db_error(e, "delete_user")
            return False

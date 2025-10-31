from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON
from datetime import datetime
from .database_manager import Base


class User(Base):
    """
    Модель пользователя для хранения в БД
    Параметры: наследует от Base
    Возвращает: экземпляр модели User
    Пример: user = User(telegram_id=123, username='test')
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    role = Column(String, default="user")


class UserMetrics(Base):
    __tablename__ = "user_metrics"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100))  # 'start', 'vpn_created', 'feature_used'
    plugin_name = Column(String(50))
    timestamp = Column(DateTime, default=datetime.now)
    meta_data = Column(JSON)

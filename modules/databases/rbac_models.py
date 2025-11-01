from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database_manager import Base

# Связующая таблика для многие-ко-многим пользователей и ролей
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('rbac_roles.id'))
)

# Связующая таблика для многие-ко-многим ролей и разрешений
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('rbac_roles.id')),
    Column('permission_id', Integer, ForeignKey('rbac_permissions.id'))
)

class RBACRole(Base):
    """Модель ролей RBAC"""
    __tablename__ = "rbac_roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, index=True)  # admin, moderator, user, vip_user
    description = Column(String(255))
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

    # Связи
    users = relationship("User", secondary=user_roles, back_populates="rbac_roles")
    permissions = relationship("RBACPermission", secondary=role_permissions, back_populates="roles")

class RBACPermission(Base):
    """Модель разрешений RBAC"""
    __tablename__ = "rbac_permissions"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, index=True)  # user.manage, plugin.install, settings.view
    description = Column(String(255))
    category = Column(String(50))  # user_management, plugin_management, system
    created_at = Column(DateTime, default=datetime.now)

    roles = relationship("RBACRole", secondary=role_permissions, back_populates="permissions")

class AuditLog(Base):
    """Модель для аудита действий администраторов"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100))  # user.created, role.assigned, plugin.installed
    resource_type = Column(String(50))  # user, role, plugin, system
    resource_id = Column(Integer, nullable=True)
    details = Column(Text)  # JSON с деталями действия
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

# Обновляем модель User для поддержки RBAC
from .models import User

# Добавляем отношения к существующей модели User
User.rbac_roles = relationship("RBACRole", secondary=user_roles, back_populates="users")

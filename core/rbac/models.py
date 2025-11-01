from datetime import datetime
from modules.databases.database_manager import Base
from sqlalchemy import (Column, Integer, String, Boolean,
                        Table, ForeignKey, DateTime, Text)

# Связующие таблицы
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('rbac_roles.id'))
)

role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('rbac_roles.id')),
    Column('permission_id', Integer, ForeignKey('rbac_permissions.id'))
)

class RBACRole(Base):
    __tablename__ = "rbac_roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, index=True)
    description = Column(String(255))
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

class RBACPermission(Base):
    __tablename__ = "rbac_permissions"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(String(255))
    category = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100))
    resource_type = Column(String(50))
    resource_id = Column(Integer, nullable=True)
    details = Column(Text)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

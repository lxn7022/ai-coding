"""RBAC 数据模型"""
from .base import Base
from .user import User
from .role import Role
from .permission import Permission
from .association import user_roles, role_permissions

__all__ = [
    "Base",
    "User",
    "Role",
    "Permission",
    "user_roles",
    "role_permissions",
]

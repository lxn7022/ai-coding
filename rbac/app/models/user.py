"""用户模型"""
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from .base import Base, BaseMixin


class User(Base, BaseMixin):
    """用户表"""
    __tablename__ = "users"

    username = Column(String(64), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(128), unique=True, index=True, nullable=True, comment="邮箱")
    hashed_password = Column(String(128), nullable=False, comment="密码哈希")
    is_active = Column(Boolean, default=True, comment="是否启用")
    display_name = Column(String(64), nullable=True, comment="显示名称")

    # 多对多：用户-角色
    roles = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

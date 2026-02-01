"""角色模型"""
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from .base import Base, BaseMixin


class Role(Base, BaseMixin):
    """角色表"""
    __tablename__ = "roles"

    code = Column(String(64), unique=True, index=True, nullable=False, comment="角色编码")
    name = Column(String(64), nullable=False, comment="角色名称")
    description = Column(Text, nullable=True, comment="角色描述")

    # 多对多：角色-用户
    users = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles",
        lazy="selectin",
    )
    # 多对多：角色-权限
    permissions = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<Role(id={self.id}, code={self.code})>"

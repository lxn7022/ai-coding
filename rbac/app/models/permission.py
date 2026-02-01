"""权限模型"""
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from .base import Base, BaseMixin


class Permission(Base, BaseMixin):
    """权限表"""
    __tablename__ = "permissions"

    code = Column(String(128), unique=True, index=True, nullable=False, comment="权限编码")
    name = Column(String(128), nullable=False, comment="权限名称")
    resource = Column(String(64), nullable=True, comment="资源类型(如 user, order)")
    action = Column(String(32), nullable=True, comment="操作(create/read/update/delete)")
    description = Column(Text, nullable=True, comment="权限描述")

    # 多对多：权限-角色
    roles = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<Permission(id={self.id}, code={self.code})>"

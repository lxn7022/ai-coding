"""权限服务核心逻辑单元测试"""
import pytest
from sqlalchemy.orm import Session

from app.schemas.permission import PermissionCreate, PermissionUpdate
from app.services import permission_service


class TestGetPermission:
    """查询权限"""

    def test_get_permission_by_id(self, test_db: Session):
        perm = permission_service.get_permission_by_id(test_db, 1)
        assert perm is not None
        assert perm.code == "user:read"

    def test_get_permission_by_id_not_found(self, test_db: Session):
        assert permission_service.get_permission_by_id(test_db, 999) is None

    def test_get_permission_by_code(self, test_db: Session):
        perm = permission_service.get_permission_by_code(test_db, "user:create")
        assert perm is not None
        assert perm.id is not None

    def test_get_permission_by_code_not_found(self, test_db: Session):
        assert permission_service.get_permission_by_code(test_db, "nonexistent") is None


class TestGetPermissions:
    """权限列表"""

    def test_get_permissions_default(self, test_db: Session):
        perms = permission_service.get_permissions(test_db)
        assert len(perms) >= 3

    def test_get_permissions_filter_resource(self, test_db: Session):
        perms = permission_service.get_permissions(test_db, resource="user")
        assert all(p.resource == "user" for p in perms)

    def test_get_permissions_skip_limit(self, test_db: Session):
        perms = permission_service.get_permissions(test_db, skip=0, limit=2)
        assert len(perms) == 2


class TestCreatePermission:
    """创建权限"""

    def test_create_permission(self, test_db: Session):
        data = PermissionCreate(
            code="order:read",
            name="订单查看",
            resource="order",
            action="read",
            description="",
        )
        perm = permission_service.create_permission(test_db, data)
        assert perm.id is not None
        assert perm.code == "order:read"
        assert perm.resource == "order"


class TestUpdatePermission:
    """更新权限"""

    def test_update_permission(self, test_db: Session):
        data = PermissionUpdate(name="用户查看权限")
        perm = permission_service.update_permission(test_db, 1, data)
        assert perm is not None
        assert perm.name == "用户查看权限"

    def test_update_permission_not_found(self, test_db: Session):
        data = PermissionUpdate(name="x")
        assert permission_service.update_permission(test_db, 999, data) is None


class TestDeletePermission:
    """删除权限"""

    def test_delete_permission(self, test_db: Session):
        data = PermissionCreate(code="temp:read", name="临时", resource="temp", action="read")
        p = permission_service.create_permission(test_db, data)
        pid = p.id
        ok = permission_service.delete_permission(test_db, pid)
        assert ok is True
        assert permission_service.get_permission_by_id(test_db, pid) is None

    def test_delete_permission_not_found(self, test_db: Session):
        assert permission_service.delete_permission(test_db, 999) is False

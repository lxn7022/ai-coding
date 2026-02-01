"""角色服务核心逻辑单元测试"""
import pytest
from sqlalchemy.orm import Session

from app.models import Role, Permission
from app.schemas.role import RoleCreate, RoleUpdate
from app.services import role_service


class TestGetRole:
    """查询角色"""

    def test_get_role_by_id(self, test_db: Session):
        role = role_service.get_role_by_id(test_db, 1)
        assert role is not None
        assert role.code == "admin"

    def test_get_role_by_id_not_found(self, test_db: Session):
        assert role_service.get_role_by_id(test_db, 999) is None

    def test_get_role_by_code(self, test_db: Session):
        role = role_service.get_role_by_code(test_db, "user")
        assert role is not None
        assert role.id is not None


class TestGetRoles:
    """角色列表"""

    def test_get_roles_default(self, test_db: Session):
        roles = role_service.get_roles(test_db)
        assert len(roles) >= 2

    def test_get_roles_skip_limit(self, test_db: Session):
        roles = role_service.get_roles(test_db, skip=0, limit=1)
        assert len(roles) == 1


class TestCreateRole:
    """创建角色"""

    def test_create_role_without_permissions(self, test_db: Session):
        data = RoleCreate(code="guest", name="访客", description="仅查看")
        role = role_service.create_role(test_db, data)
        assert role.id is not None
        assert role.code == "guest"
        assert role.permissions == [] or len(role.permissions) == 0

    def test_create_role_with_permissions(self, test_db: Session):
        data = RoleCreate(code="editor", name="编辑", permission_ids=[1, 2])
        role = role_service.create_role(test_db, data)
        assert role.id is not None
        assert len(role.permissions) == 2
        perm_codes = {p.code for p in role.permissions}
        assert "user:read" in perm_codes
        assert "user:create" in perm_codes


class TestUpdateRole:
    """更新角色"""

    def test_update_role(self, test_db: Session):
        data = RoleUpdate(name="超级管理员")
        role = role_service.update_role(test_db, 1, data)
        assert role is not None
        assert role.name == "超级管理员"

    def test_update_role_not_found(self, test_db: Session):
        data = RoleUpdate(name="x")
        assert role_service.update_role(test_db, 999, data) is None

    def test_update_role_permission_ids(self, test_db: Session):
        # 将 admin 角色的权限改为仅 [1]
        data = RoleUpdate(permission_ids=[1])
        role = role_service.update_role(test_db, 1, data)
        assert role is not None
        assert len(role.permissions) == 1
        assert role.permissions[0].code == "user:read"


class TestDeleteRole:
    """删除角色"""

    def test_delete_role(self, test_db: Session):
        data = RoleCreate(code="todelete", name="待删")
        r = role_service.create_role(test_db, data)
        rid = r.id
        ok = role_service.delete_role(test_db, rid)
        assert ok is True
        assert role_service.get_role_by_id(test_db, rid) is None

    def test_delete_role_not_found(self, test_db: Session):
        assert role_service.delete_role(test_db, 999) is False

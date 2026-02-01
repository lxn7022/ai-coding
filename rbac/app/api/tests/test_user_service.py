"""用户服务核心逻辑单元测试"""
import pytest
from sqlalchemy.orm import Session

from app.models import User, Role
from app.schemas.user import UserCreate, UserUpdate
from app.services import user_service


class TestGetUser:
    """查询用户"""

    def test_get_user_by_id(self, test_db: Session):
        user = user_service.get_user_by_id(test_db, 1)
        assert user is not None
        assert user.id == 1
        assert user.username == "admin"

    def test_get_user_by_id_not_found(self, test_db: Session):
        assert user_service.get_user_by_id(test_db, 999) is None

    def test_get_user_by_username(self, test_db: Session):
        user = user_service.get_user_by_username(test_db, "user1")
        assert user is not None
        assert user.username == "user1"

    def test_get_user_by_username_not_found(self, test_db: Session):
        assert user_service.get_user_by_username(test_db, "nonexistent") is None


class TestGetUsers:
    """用户列表（分页与筛选）"""

    def test_get_users_default(self, test_db: Session):
        users = user_service.get_users(test_db)
        assert len(users) >= 2

    def test_get_users_with_skip_limit(self, test_db: Session):
        users = user_service.get_users(test_db, skip=0, limit=1)
        assert len(users) == 1

    def test_get_users_keyword_username(self, test_db: Session):
        users = user_service.get_users(test_db, keyword="admin")
        assert len(users) >= 1
        assert any(u.username == "admin" for u in users)

    def test_get_users_keyword_display_name(self, test_db: Session):
        users = user_service.get_users(test_db, keyword="用户1")
        assert len(users) >= 1
        assert any(u.display_name == "用户1" for u in users)

    def test_get_users_filter_is_active(self, test_db: Session):
        users = user_service.get_users(test_db, is_active=True)
        assert all(u.is_active for u in users)


class TestCreateUser:
    """创建用户"""

    def test_create_user(self, test_db: Session):
        data = UserCreate(
            username="newuser",
            email="new@test.com",
            display_name="新用户",
            password="password123",
        )
        user = user_service.create_user(test_db, data)
        assert user.id is not None
        assert user.username == "newuser"
        assert user.email == "new@test.com"
        assert user.display_name == "新用户"
        assert user.hashed_password != "password123"

    def test_create_user_display_name_defaults_to_username(self, test_db: Session):
        data = UserCreate(username="nodisplay", password="pass1234")
        user = user_service.create_user(test_db, data)
        assert user.display_name == "nodisplay"


class TestUpdateUser:
    """更新用户"""

    def test_update_user(self, test_db: Session):
        data = UserUpdate(display_name="更新后的名称")
        user = user_service.update_user(test_db, 1, data)
        assert user is not None
        assert user.display_name == "更新后的名称"

    def test_update_user_not_found(self, test_db: Session):
        data = UserUpdate(display_name="x")
        assert user_service.update_user(test_db, 999, data) is None

    def test_update_user_password(self, test_db: Session):
        data = UserUpdate(password="newpass123")
        user = user_service.update_user(test_db, 1, data)
        assert user is not None
        from app.auth import verify_password
        assert verify_password("newpass123", user.hashed_password) is True


class TestAssignRolesToUser:
    """为用户分配角色"""

    def test_assign_roles_to_user(self, test_db: Session):
        # user1 当前有 user 角色，改为只保留 admin 角色（id=1）
        user = user_service.assign_roles_to_user(test_db, 2, [1])
        assert user is not None
        role_codes = [r.code for r in user.roles]
        assert "admin" in role_codes

    def test_assign_roles_to_user_not_found(self, test_db: Session):
        assert user_service.assign_roles_to_user(test_db, 999, [1]) is None


class TestDeleteUser:
    """删除用户"""

    def test_delete_user(self, test_db: Session):
        # 先创建一个用户再删除
        data = UserCreate(username="todelete", password="pass1234")
        u = user_service.create_user(test_db, data)
        uid = u.id
        ok = user_service.delete_user(test_db, uid)
        assert ok is True
        assert user_service.get_user_by_id(test_db, uid) is None

    def test_delete_user_not_found(self, test_db: Session):
        assert user_service.delete_user(test_db, 999) is False

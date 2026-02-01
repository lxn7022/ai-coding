"""认证与权限逻辑单元测试：密码、JWT、用户权限码"""
import pytest
from datetime import timedelta
from sqlalchemy.orm import Session

from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_token,
    get_user_permission_codes,
)
from app.models import User, Role, Permission


class TestPassword:
    """密码哈希与验证"""

    def test_hash_and_verify(self):
        plain = "secret123"
        hashed = get_password_hash(plain)
        assert hashed != plain
        assert verify_password(plain, hashed) is True

    def test_verify_wrong_password(self):
        hashed = get_password_hash("secret123")
        assert verify_password("wrong", hashed) is False

    def test_different_hashes_for_same_password(self):
        h1 = get_password_hash("same")
        h2 = get_password_hash("same")
        assert h1 != h2
        assert verify_password("same", h1) and verify_password("same", h2)


class TestJWT:
    """JWT 生成与解析"""

    def test_create_and_decode(self):
        payload = {"sub": "123", "extra": "ok"}
        token = create_access_token(payload)
        assert isinstance(token, str)
        decoded = decode_token(token)
        assert decoded is not None
        assert decoded.get("sub") == "123"
        assert decoded.get("extra") == "ok"
        assert "exp" in decoded

    def test_decode_invalid_token(self):
        assert decode_token("invalid.token.here") is None
        assert decode_token("") is None

    def test_create_with_expires_delta(self):
        payload = {"sub": "1"}
        token = create_access_token(payload, expires_delta=timedelta(minutes=5))
        decoded = decode_token(token)
        assert decoded is not None
        assert decoded["sub"] == "1"


class TestGetUserPermissionCodes:
    """用户权限码聚合（多角色去重）"""

    def test_no_roles(self):
        user = User(username="u", hashed_password="x", roles=[])
        assert get_user_permission_codes(user) == []

    def test_single_role(self):
        p1 = Permission(code="a:read", name="", resource="a", action="read", description=None)
        role = Role(code="r", name="R", permissions=[p1])
        user = User(username="u", hashed_password="x", roles=[role])
        assert set(get_user_permission_codes(user)) == {"a:read"}

    def test_multiple_roles_dedupe(self):
        p1 = Permission(code="a:read", name="", resource="a", action="read", description=None)
        p2 = Permission(code="a:write", name="", resource="a", action="write", description=None)
        r1 = Role(code="r1", name="R1", permissions=[p1])
        r2 = Role(code="r2", name="R2", permissions=[p1, p2])
        user = User(username="u", hashed_password="x", roles=[r1, r2])
        assert set(get_user_permission_codes(user)) == {"a:read", "a:write"}

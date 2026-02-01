"""公共 fixture：测试数据库、客户端、种子数据"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.models import Base, User, Role, Permission
from app.database import get_db
from app.main import app
from app.auth import get_password_hash


def _seed_db(db: Session) -> tuple[User, Role, Permission]:
    """往数据库写入权限、角色、用户，返回 (admin_user, admin_role, perm_example)。"""
    p1 = Permission(code="user:read", name="用户查看", resource="user", action="read", description="")
    p2 = Permission(code="user:create", name="用户创建", resource="user", action="create", description="")
    p3 = Permission(code="role:read", name="角色查看", resource="role", action="read", description="")
    db.add_all([p1, p2, p3])
    db.flush()

    admin_role = Role(code="admin", name="管理员", description="", permissions=[p1, p2, p3])
    user_role = Role(code="user", name="普通用户", description="", permissions=[p1, p3])
    db.add(admin_role)
    db.add(user_role)
    db.flush()

    admin_user = User(
        username="admin",
        email="admin@test.com",
        display_name="管理员",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
        roles=[admin_role],
    )
    normal_user = User(
        username="user1",
        email="user1@test.com",
        display_name="用户1",
        hashed_password=get_password_hash("pass123"),
        is_active=True,
        roles=[user_role],
    )
    db.add(admin_user)
    db.add(normal_user)
    db.commit()
    db.refresh(admin_user)
    db.refresh(admin_role)
    db.refresh(p1)
    return admin_user, admin_role, p1


@pytest.fixture
def test_db() -> Session:
    """每个测试独立的 in-memory 数据库会话，并已 seed 权限/角色/用户。"""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    _seed_db(session)
    yield session
    session.close()


@pytest.fixture
def client(test_db: Session):
    """FastAPI TestClient，get_db 使用 test_db。"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client, test_db: Session):
    """使用 admin/admin123 登录后得到的 Authorization 头。"""
    r = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_user1(client, test_db: Session):
    """使用 user1/pass123 登录后得到的 Authorization 头（权限少于 admin）。"""
    r = client.post("/api/auth/login", json={"username": "user1", "password": "pass123"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

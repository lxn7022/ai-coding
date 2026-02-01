"""测试 fixture：内存数据库与会话"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.models import Base, User, Role, Permission
from app.auth import get_password_hash


def _seed_db(db: Session) -> tuple[User, Role, Permission]:
    """写入权限、角色、用户，返回 (admin_user, admin_role, perm_example)。"""
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

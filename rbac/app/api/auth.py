"""认证接口：登录、当前用户"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserLogin, UserResponse, Token
from app.auth import verify_password, create_access_token, get_current_user
from app.models import User
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """登录，返回 JWT 及用户信息"""
    user = user_service.get_user_by_username(db, data.username)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="用户已禁用")
    token = create_access_token(data={"sub": str(user.id)})
    from app.schemas.role import RoleResponse
    from app.schemas.permission import PermissionResponse
    roles = [
        RoleResponse(
            id=r.id, code=r.code, name=r.name, description=r.description,
            created_at=r.created_at, updated_at=r.updated_at,
            permissions=[PermissionResponse(
                id=p.id, code=p.code, name=p.name, resource=p.resource,
                action=p.action, description=p.description,
                created_at=p.created_at, updated_at=p.updated_at,
            ) for p in r.permissions],
        )
        for r in user.roles
    ]
    user_resp = UserResponse(
        id=user.id, username=user.username, email=user.email,
        display_name=user.display_name, is_active=user.is_active,
        created_at=user.created_at, updated_at=user.updated_at,
        roles=roles,
    )
    return Token(access_token=token, user=user_resp)


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    """获取当前登录用户信息（需携带 Bearer Token）"""
    from app.schemas.role import RoleResponse
    from app.schemas.permission import PermissionResponse
    roles = [
        RoleResponse(
            id=r.id, code=r.code, name=r.name, description=r.description,
            created_at=r.created_at, updated_at=r.updated_at,
            permissions=[PermissionResponse(
                id=p.id, code=p.code, name=p.name, resource=p.resource,
                action=p.action, description=p.description,
                created_at=p.created_at, updated_at=p.updated_at,
            ) for p in r.permissions],
        )
        for r in user.roles
    ]
    return UserResponse(
        id=user.id, username=user.username, email=user.email,
        display_name=user.display_name, is_active=user.is_active,
        created_at=user.created_at, updated_at=user.updated_at,
        roles=roles,
    )

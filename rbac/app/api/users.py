"""用户管理接口（需权限）"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.role import RoleAssign
from app.schemas.role import RoleResponse
from app.schemas.permission import PermissionResponse
from app.auth import get_current_user, require_permissions
from app.services import user_service

router = APIRouter(prefix="/users", tags=["用户管理"])


def _user_to_response(user: User) -> UserResponse:
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


@router.get("", response_model=List[UserResponse])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_permissions("user:read", "user:list")),
):
    """用户列表（需 user:read 或 user:list）"""
    users = user_service.get_users(db, skip=skip, limit=limit, keyword=keyword, is_active=is_active)
    return [_user_to_response(u) for u in users]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permissions("user:create")),
):
    """创建用户（需 user:create）"""
    if user_service.get_user_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    u = user_service.create_user(db, data)
    return _user_to_response(u)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(require_permissions("user:read", "user:list")),
):
    """用户详情（需 user:read 或 user:list）"""
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return _user_to_response(user)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(require_permissions("user:update")),
):
    """更新用户（需 user:update）"""
    user = user_service.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return _user_to_response(user)


@router.post("/{user_id}/roles", response_model=UserResponse)
def assign_user_roles(
    user_id: int,
    data: RoleAssign,
    db: Session = Depends(get_db),
    current: User = Depends(require_permissions("user:assign_roles", "role:assign")),
):
    """为用户分配角色（需 user:assign_roles 或 role:assign）"""
    user = user_service.assign_roles_to_user(db, user_id, data.role_ids)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return _user_to_response(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(require_permissions("user:delete")),
):
    """删除用户（需 user:delete）"""
    if not user_service.delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="用户不存在")

"""角色管理接口"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from app.schemas.permission import PermissionResponse
from app.auth import get_current_user, require_permissions
from app.services import role_service

router = APIRouter(prefix="/roles", tags=["角色管理"])


def _role_to_response(role) -> RoleResponse:
    return RoleResponse(
        id=role.id, code=role.code, name=role.name, description=role.description,
        created_at=role.created_at, updated_at=role.updated_at,
        permissions=[
            PermissionResponse(
                id=p.id, code=p.code, name=p.name, resource=p.resource,
                action=p.action, description=p.description,
                created_at=p.created_at, updated_at=p.updated_at,
            )
            for p in role.permissions
        ],
    )


@router.get("", response_model=List[RoleResponse])
def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(require_permissions("role:read", "role:list")),
):
    """角色列表（需 role:read 或 role:list）"""
    roles = role_service.get_roles(db, skip=skip, limit=limit)
    return [_role_to_response(r) for r in roles]


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    data: RoleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permissions("role:create")),
):
    """创建角色（需 role:create）"""
    if role_service.get_role_by_code(db, data.code):
        raise HTTPException(status_code=400, detail="角色编码已存在")
    role = role_service.create_role(db, data)
    return _role_to_response(role)


@router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_permissions("role:read", "role:list")),
):
    """角色详情"""
    role = role_service.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    return _role_to_response(role)


@router.patch("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    data: RoleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permissions("role:update")),
):
    """更新角色（需 role:update）"""
    role = role_service.update_role(db, role_id, data)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    return _role_to_response(role)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_permissions("role:delete")),
):
    """删除角色（需 role:delete）"""
    if not role_service.delete_role(db, role_id):
        raise HTTPException(status_code=404, detail="角色不存在")

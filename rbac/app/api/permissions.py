"""权限管理接口"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.permission import PermissionCreate, PermissionUpdate, PermissionResponse
from app.auth import get_current_user, require_permissions
from app.services import permission_service

router = APIRouter(prefix="/permissions", tags=["权限管理"])


@router.get("", response_model=List[PermissionResponse])
def list_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    resource: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_permissions("permission:read", "permission:list")),
):
    """权限列表（需 permission:read 或 permission:list）"""
    perms = permission_service.get_permissions(db, skip=skip, limit=limit, resource=resource)
    return [
        PermissionResponse(
            id=p.id, code=p.code, name=p.name, resource=p.resource,
            action=p.action, description=p.description,
            created_at=p.created_at, updated_at=p.updated_at,
        )
        for p in perms
    ]


@router.post("", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(
    data: PermissionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permissions("permission:create")),
):
    """创建权限（需 permission:create）"""
    if permission_service.get_permission_by_code(db, data.code):
        raise HTTPException(status_code=400, detail="权限编码已存在")
    perm = permission_service.create_permission(db, data)
    return PermissionResponse(
        id=perm.id, code=perm.code, name=perm.name, resource=perm.resource,
        action=perm.action, description=perm.description,
        created_at=perm.created_at, updated_at=perm.updated_at,
    )


@router.get("/{perm_id}", response_model=PermissionResponse)
def get_permission(
    perm_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_permissions("permission:read", "permission:list")),
):
    """权限详情"""
    perm = permission_service.get_permission_by_id(db, perm_id)
    if not perm:
        raise HTTPException(status_code=404, detail="权限不存在")
    return PermissionResponse(
        id=perm.id, code=perm.code, name=perm.name, resource=perm.resource,
        action=perm.action, description=perm.description,
        created_at=perm.created_at, updated_at=perm.updated_at,
    )


@router.patch("/{perm_id}", response_model=PermissionResponse)
def update_permission(
    perm_id: int,
    data: PermissionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permissions("permission:update")),
):
    """更新权限（需 permission:update）"""
    perm = permission_service.update_permission(db, perm_id, data)
    if not perm:
        raise HTTPException(status_code=404, detail="权限不存在")
    return PermissionResponse(
        id=perm.id, code=perm.code, name=perm.name, resource=perm.resource,
        action=perm.action, description=perm.description,
        created_at=perm.created_at, updated_at=perm.updated_at,
    )


@router.delete("/{perm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permission(
    perm_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_permissions("permission:delete")),
):
    """删除权限（需 permission:delete）"""
    if not permission_service.delete_permission(db, perm_id):
        raise HTTPException(status_code=404, detail="权限不存在")

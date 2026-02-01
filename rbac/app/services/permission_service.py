"""权限服务"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models import Permission
from app.schemas.permission import PermissionCreate, PermissionUpdate


def get_permission_by_id(db: Session, perm_id: int) -> Optional[Permission]:
    return db.query(Permission).filter(Permission.id == perm_id).first()


def get_permission_by_code(db: Session, code: str) -> Optional[Permission]:
    return db.query(Permission).filter(Permission.code == code).first()


def get_permissions(
    db: Session,
    skip: int = 0,
    limit: int = 200,
    resource: Optional[str] = None,
) -> List[Permission]:
    q = db.query(Permission)
    if resource:
        q = q.filter(Permission.resource == resource)
    return q.offset(skip).limit(limit).all()


def create_permission(db: Session, data: PermissionCreate) -> Permission:
    perm = Permission(
        code=data.code,
        name=data.name,
        resource=data.resource,
        action=data.action,
        description=data.description,
    )
    db.add(perm)
    db.commit()
    db.refresh(perm)
    return perm


def update_permission(db: Session, perm_id: int, data: PermissionUpdate) -> Optional[Permission]:
    perm = get_permission_by_id(db, perm_id)
    if not perm:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(perm, k, v)
    db.commit()
    db.refresh(perm)
    return perm


def delete_permission(db: Session, perm_id: int) -> bool:
    perm = get_permission_by_id(db, perm_id)
    if not perm:
        return False
    db.delete(perm)
    db.commit()
    return True

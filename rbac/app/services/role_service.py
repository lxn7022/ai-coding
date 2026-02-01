"""角色服务"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models import Role, Permission
from app.schemas.role import RoleCreate, RoleUpdate


def get_role_by_id(db: Session, role_id: int) -> Optional[Role]:
    return db.query(Role).filter(Role.id == role_id).first()


def get_role_by_code(db: Session, code: str) -> Optional[Role]:
    return db.query(Role).filter(Role.code == code).first()


def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
    return db.query(Role).offset(skip).limit(limit).all()


def create_role(db: Session, data: RoleCreate) -> Role:
    role = Role(code=data.code, name=data.name, description=data.description)
    db.add(role)
    db.flush()
    if data.permission_ids:
        perms = db.query(Permission).filter(Permission.id.in_(data.permission_ids)).all()
        role.permissions = perms
    db.commit()
    db.refresh(role)
    return role


def update_role(db: Session, role_id: int, data: RoleUpdate) -> Optional[Role]:
    role = get_role_by_id(db, role_id)
    if not role:
        return None
    update = data.model_dump(exclude_unset=True)
    permission_ids = update.pop("permission_ids", None)
    for k, v in update.items():
        setattr(role, k, v)
    if permission_ids is not None:
        role.permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
    db.commit()
    db.refresh(role)
    return role


def delete_role(db: Session, role_id: int) -> bool:
    role = get_role_by_id(db, role_id)
    if not role:
        return False
    db.delete(role)
    db.commit()
    return True

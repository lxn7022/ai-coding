"""用户服务"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models import User, Role
from app.schemas.user import UserCreate, UserUpdate
from app.auth import get_password_hash


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    keyword: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> List[User]:
    q = db.query(User)
    if keyword:
        q = q.filter(
            or_(
                User.username.ilike(f"%{keyword}%"),
                User.display_name.ilike(f"%{keyword}%"),
                User.email.ilike(f"%{keyword}%"),
            )
        )
    if is_active is not None:
        q = q.filter(User.is_active == is_active)
    return q.offset(skip).limit(limit).all()


def create_user(db: Session, data: UserCreate) -> User:
    user = User(
        username=data.username,
        email=data.email,
        display_name=data.display_name or data.username,
        hashed_password=get_password_hash(data.password),
        is_active=data.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, data: UserUpdate) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    update = data.model_dump(exclude_unset=True)
    if "password" in update and update["password"]:
        update["hashed_password"] = get_password_hash(update.pop("password"))
    for k, v in update.items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user


def assign_roles_to_user(db: Session, user_id: int, role_ids: List[int]) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
    user.roles = roles
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True

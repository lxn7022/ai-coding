"""认证与权限校验"""
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


def verify_password(plain: str, hashed: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    """密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """生成 JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """解析 JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """依赖：从 Bearer Token 获取当前用户"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证信息",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或过期的令牌",
        )
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="无效的令牌载荷")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="用户已禁用")
    return user


def get_user_permission_codes(user: User) -> List[str]:
    """获取用户拥有的所有权限编码（去重）"""
    codes = set()
    for role in user.roles:
        for perm in role.permissions:
            codes.add(perm.code)
    return list(codes)


def require_permissions(*permission_codes: str):
    """依赖：要求当前用户拥有给定权限中的至少一个"""
    async def _check(user: User = Depends(get_current_user)) -> User:
        user_codes = get_user_permission_codes(user)
        if not permission_codes:
            return user
        if any(code in user_codes for code in permission_codes):
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，需要以下权限之一: {', '.join(permission_codes)}",
        )
    return _check


def require_any_permission(*permission_codes: str):
    """与 require_permissions 相同，语义化别名"""
    return require_permissions(*permission_codes)


def require_all_permissions(*permission_codes: str):
    """依赖：要求当前用户拥有全部给定权限"""
    async def _check(user: User = Depends(get_current_user)) -> User:
        user_codes = get_user_permission_codes(user)
        missing = [c for c in permission_codes if c not in user_codes]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，缺少: {', '.join(missing)}",
            )
        return user
    return _check

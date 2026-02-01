"""角色相关 Schema"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., max_length=64)
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permission_ids: List[int] = Field(default_factory=list, description="权限ID列表")


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None


class RoleResponse(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    permissions: List["PermissionResponse"] = []

    class Config:
        from_attributes = True


class RoleAssign(BaseModel):
    """为用户分配角色"""
    role_ids: List[int] = Field(..., min_length=1)


from .permission import PermissionResponse
RoleResponse.model_rebuild()

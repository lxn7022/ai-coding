package models

// Role 角色模型
type Role struct {
	BaseModel
	Name        string       `json:"name" gorm:"size:50;not null"`
	Code        string       `json:"code" gorm:"uniqueIndex;size:50;not null"`
	Description string       `json:"description" gorm:"size:255"`
	Status      int          `json:"status" gorm:"default:1"` // 1: 启用, 0: 禁用
	Permissions []Permission `json:"permissions" gorm:"many2many:role_permissions;"`
	Users       []User       `json:"-" gorm:"many2many:user_roles;"`
}

// TableName 指定表名
func (Role) TableName() string {
	return "roles"
}

// CreateRoleRequest 创建角色请求
type CreateRoleRequest struct {
	Name        string `json:"name" binding:"required,max=50"`
	Code        string `json:"code" binding:"required,max=50"`
	Description string `json:"description" binding:"omitempty,max=255"`
}

// UpdateRoleRequest 更新角色请求
type UpdateRoleRequest struct {
	Name        string `json:"name" binding:"omitempty,max=50"`
	Description string `json:"description" binding:"omitempty,max=255"`
	Status      *int   `json:"status" binding:"omitempty,oneof=0 1"`
}

// AssignPermissionsRequest 分配权限请求
type AssignPermissionsRequest struct {
	PermissionIDs []uint `json:"permission_ids" binding:"required"`
}

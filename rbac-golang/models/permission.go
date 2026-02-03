package models

// Permission 权限模型
type Permission struct {
	BaseModel
	Name        string `json:"name" gorm:"size:50;not null"`
	Code        string `json:"code" gorm:"uniqueIndex;size:100;not null"`
	Type        string `json:"type" gorm:"size:20;not null"` // menu: 菜单, button: 按钮, api: 接口
	Path        string `json:"path" gorm:"size:255"`         // API路径或菜单路径
	Method      string `json:"method" gorm:"size:10"`        // HTTP方法: GET, POST, PUT, DELETE
	ParentID    *uint  `json:"parent_id" gorm:"index"`
	Description string `json:"description" gorm:"size:255"`
	Status      int    `json:"status" gorm:"default:1"` // 1: 启用, 0: 禁用
	Sort        int    `json:"sort" gorm:"default:0"`   // 排序
}

// TableName 指定表名
func (Permission) TableName() string {
	return "permissions"
}

// CreatePermissionRequest 创建权限请求
type CreatePermissionRequest struct {
	Name        string `json:"name" binding:"required,max=50"`
	Code        string `json:"code" binding:"required,max=100"`
	Type        string `json:"type" binding:"required,oneof=menu button api"`
	Path        string `json:"path" binding:"omitempty,max=255"`
	Method      string `json:"method" binding:"omitempty,oneof=GET POST PUT DELETE PATCH"`
	ParentID    *uint  `json:"parent_id"`
	Description string `json:"description" binding:"omitempty,max=255"`
	Sort        int    `json:"sort"`
}

// UpdatePermissionRequest 更新权限请求
type UpdatePermissionRequest struct {
	Name        string `json:"name" binding:"omitempty,max=50"`
	Path        string `json:"path" binding:"omitempty,max=255"`
	Method      string `json:"method" binding:"omitempty,oneof=GET POST PUT DELETE PATCH"`
	ParentID    *uint  `json:"parent_id"`
	Description string `json:"description" binding:"omitempty,max=255"`
	Status      *int   `json:"status" binding:"omitempty,oneof=0 1"`
	Sort        *int   `json:"sort"`
}

// PermissionTree 权限树结构
type PermissionTree struct {
	Permission
	Children []PermissionTree `json:"children"`
}

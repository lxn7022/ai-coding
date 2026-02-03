package models

import (
	"golang.org/x/crypto/bcrypt"
	"gorm.io/gorm"
)

// User 用户模型
type User struct {
	BaseModel
	Username string `json:"username" gorm:"uniqueIndex;size:50;not null"`
	Password string `json:"-" gorm:"size:255;not null"`
	Email    string `json:"email" gorm:"uniqueIndex;size:100"`
	Nickname string `json:"nickname" gorm:"size:50"`
	Status   int    `json:"status" gorm:"default:1"` // 1: 启用, 0: 禁用
	Roles    []Role `json:"roles" gorm:"many2many:user_roles;"`
}

// TableName 指定表名
func (User) TableName() string {
	return "users"
}

// BeforeCreate 创建前钩子，对密码进行加密
func (u *User) BeforeCreate(tx *gorm.DB) error {
	return u.hashPassword()
}

// hashPassword 加密密码
func (u *User) hashPassword() error {
	if u.Password != "" {
		hashedPassword, err := bcrypt.GenerateFromPassword([]byte(u.Password), bcrypt.DefaultCost)
		if err != nil {
			return err
		}
		u.Password = string(hashedPassword)
	}
	return nil
}

// CheckPassword 校验密码
func (u *User) CheckPassword(password string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(u.Password), []byte(password))
	return err == nil
}

// SetPassword 设置密码（用于更新密码）
func (u *User) SetPassword(password string) error {
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return err
	}
	u.Password = string(hashedPassword)
	return nil
}

// HasPermission 检查用户是否拥有指定权限
func (u *User) HasPermission(permissionCode string) bool {
	for _, role := range u.Roles {
		for _, perm := range role.Permissions {
			if perm.Code == permissionCode {
				return true
			}
		}
	}
	return false
}

// HasRole 检查用户是否拥有指定角色
func (u *User) HasRole(roleCode string) bool {
	for _, role := range u.Roles {
		if role.Code == roleCode {
			return true
		}
	}
	return false
}

// CreateUserRequest 创建用户请求
type CreateUserRequest struct {
	Username string `json:"username" binding:"required,min=3,max=50"`
	Password string `json:"password" binding:"required,min=6,max=50"`
	Email    string `json:"email" binding:"omitempty,email"`
	Nickname string `json:"nickname" binding:"omitempty,max=50"`
}

// UpdateUserRequest 更新用户请求
type UpdateUserRequest struct {
	Email    string `json:"email" binding:"omitempty,email"`
	Nickname string `json:"nickname" binding:"omitempty,max=50"`
	Status   *int   `json:"status" binding:"omitempty,oneof=0 1"`
}

// LoginRequest 登录请求
type LoginRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

// LoginResponse 登录响应
type LoginResponse struct {
	Token string `json:"token"`
	User  User   `json:"user"`
}

// AssignRolesRequest 分配角色请求
type AssignRolesRequest struct {
	RoleIDs []uint `json:"role_ids" binding:"required"`
}

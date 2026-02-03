package database

import (
	"log"
	"rbac-golang/config"
	"rbac-golang/models"

	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

var DB *gorm.DB

// InitDB 初始化数据库连接
func InitDB(cfg *config.Config) error {
	var err error

	// 配置GORM日志
	gormConfig := &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
	}

	// 根据配置选择数据库驱动
	switch cfg.Database.Driver {
	case "sqlite":
		DB, err = gorm.Open(sqlite.Open(cfg.Database.DSN), gormConfig)
	default:
		DB, err = gorm.Open(sqlite.Open(cfg.Database.DSN), gormConfig)
	}

	if err != nil {
		return err
	}

	// 自动迁移数据库表结构
	err = DB.AutoMigrate(
		&models.User{},
		&models.Role{},
		&models.Permission{},
	)
	if err != nil {
		return err
	}

	log.Println("数据库连接成功，表结构已同步")
	return nil
}

// InitDefaultData 初始化默认数据
func InitDefaultData() error {
	// 检查是否已有管理员用户
	var adminCount int64
	DB.Model(&models.User{}).Where("username = ?", "admin").Count(&adminCount)
	if adminCount > 0 {
		log.Println("默认数据已存在，跳过初始化")
		return nil
	}

	// 创建默认权限
	permissions := []models.Permission{
		// 用户管理权限
		{Name: "用户管理", Code: "user:manage", Type: "menu", Path: "/users", Description: "用户管理菜单"},
		{Name: "查看用户", Code: "user:list", Type: "api", Path: "/api/v1/users", Method: "GET", Description: "查看用户列表"},
		{Name: "创建用户", Code: "user:create", Type: "api", Path: "/api/v1/users", Method: "POST", Description: "创建新用户"},
		{Name: "更新用户", Code: "user:update", Type: "api", Path: "/api/v1/users/:id", Method: "PUT", Description: "更新用户信息"},
		{Name: "删除用户", Code: "user:delete", Type: "api", Path: "/api/v1/users/:id", Method: "DELETE", Description: "删除用户"},
		// 角色管理权限
		{Name: "角色管理", Code: "role:manage", Type: "menu", Path: "/roles", Description: "角色管理菜单"},
		{Name: "查看角色", Code: "role:list", Type: "api", Path: "/api/v1/roles", Method: "GET", Description: "查看角色列表"},
		{Name: "创建角色", Code: "role:create", Type: "api", Path: "/api/v1/roles", Method: "POST", Description: "创建新角色"},
		{Name: "更新角色", Code: "role:update", Type: "api", Path: "/api/v1/roles/:id", Method: "PUT", Description: "更新角色信息"},
		{Name: "删除角色", Code: "role:delete", Type: "api", Path: "/api/v1/roles/:id", Method: "DELETE", Description: "删除角色"},
		// 权限管理权限
		{Name: "权限管理", Code: "permission:manage", Type: "menu", Path: "/permissions", Description: "权限管理菜单"},
		{Name: "查看权限", Code: "permission:list", Type: "api", Path: "/api/v1/permissions", Method: "GET", Description: "查看权限列表"},
		{Name: "创建权限", Code: "permission:create", Type: "api", Path: "/api/v1/permissions", Method: "POST", Description: "创建新权限"},
		{Name: "更新权限", Code: "permission:update", Type: "api", Path: "/api/v1/permissions/:id", Method: "PUT", Description: "更新权限信息"},
		{Name: "删除权限", Code: "permission:delete", Type: "api", Path: "/api/v1/permissions/:id", Method: "DELETE", Description: "删除权限"},
	}

	if err := DB.Create(&permissions).Error; err != nil {
		return err
	}

	// 创建管理员角色
	adminRole := models.Role{
		Name:        "超级管理员",
		Code:        "admin",
		Description: "系统超级管理员，拥有所有权限",
		Permissions: permissions,
	}
	if err := DB.Create(&adminRole).Error; err != nil {
		return err
	}

	// 创建普通用户角色
	userPermissions := []models.Permission{}
	DB.Where("code IN ?", []string{"user:list", "role:list", "permission:list"}).Find(&userPermissions)
	
	userRole := models.Role{
		Name:        "普通用户",
		Code:        "user",
		Description: "普通用户，仅有查看权限",
		Permissions: userPermissions,
	}
	if err := DB.Create(&userRole).Error; err != nil {
		return err
	}

	// 创建管理员用户
	adminUser := models.User{
		Username: "admin",
		Password: "admin123",
		Email:    "admin@example.com",
		Nickname: "系统管理员",
		Roles:    []models.Role{adminRole},
	}
	if err := DB.Create(&adminUser).Error; err != nil {
		return err
	}

	log.Println("默认数据初始化完成")
	log.Println("管理员账号: admin / admin123")
	return nil
}

// GetDB 获取数据库实例
func GetDB() *gorm.DB {
	return DB
}

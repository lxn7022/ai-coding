package tests

import (
	"rbac-golang/config"
	"rbac-golang/database"
	"rbac-golang/models"
	"rbac-golang/routes"

	"github.com/gin-gonic/gin"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

// TestConfig 测试配置
func TestConfig() *config.Config {
	return &config.Config{
		Server: config.ServerConfig{
			Port: "8080",
			Mode: "test",
		},
		Database: config.DatabaseConfig{
			Driver: "sqlite",
			DSN:    ":memory:",
		},
		JWT: config.JWTConfig{
			Secret:     "test-secret-key",
			ExpireTime: 24 * 60 * 60 * 1000000000, // 24小时
		},
	}
}

// SetupTestDB 初始化测试数据库
func SetupTestDB() (*gorm.DB, error) {
	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Silent),
	})
	if err != nil {
		return nil, err
	}

	// 迁移表结构
	err = db.AutoMigrate(
		&models.User{},
		&models.Role{},
		&models.Permission{},
	)
	if err != nil {
		return nil, err
	}

	// 设置全局数据库实例
	database.DB = db

	return db, nil
}

// SetupTestRouter 创建测试路由
func SetupTestRouter() *gin.Engine {
	gin.SetMode(gin.TestMode)
	cfg := TestConfig()
	return routes.SetupRouter(cfg)
}

// CreateTestData 创建测试数据
func CreateTestData(db *gorm.DB) (*models.User, *models.Role, []models.Permission, error) {
	// 创建测试权限
	permissions := []models.Permission{
		{Name: "查看用户", Code: "user:list", Type: "api", Path: "/api/v1/users", Method: "GET"},
		{Name: "创建用户", Code: "user:create", Type: "api", Path: "/api/v1/users", Method: "POST"},
		{Name: "更新用户", Code: "user:update", Type: "api", Path: "/api/v1/users/:id", Method: "PUT"},
		{Name: "删除用户", Code: "user:delete", Type: "api", Path: "/api/v1/users/:id", Method: "DELETE"},
		{Name: "查看角色", Code: "role:list", Type: "api", Path: "/api/v1/roles", Method: "GET"},
		{Name: "查看权限", Code: "permission:list", Type: "api", Path: "/api/v1/permissions", Method: "GET"},
	}
	if err := db.Create(&permissions).Error; err != nil {
		return nil, nil, nil, err
	}

	// 创建管理员角色
	adminRole := models.Role{
		Name:        "管理员",
		Code:        "admin",
		Description: "系统管理员",
		Permissions: permissions,
	}
	if err := db.Create(&adminRole).Error; err != nil {
		return nil, nil, nil, err
	}

	// 创建普通用户角色（只有查看权限）
	var viewPermissions []models.Permission
	db.Where("code IN ?", []string{"user:list", "role:list", "permission:list"}).Find(&viewPermissions)

	userRole := models.Role{
		Name:        "普通用户",
		Code:        "user",
		Description: "普通用户",
		Permissions: viewPermissions,
	}
	if err := db.Create(&userRole).Error; err != nil {
		return nil, nil, nil, err
	}

	// 创建管理员用户
	adminUser := models.User{
		Username: "admin",
		Password: "admin123",
		Email:    "admin@test.com",
		Nickname: "管理员",
		Roles:    []models.Role{adminRole},
	}
	if err := db.Create(&adminUser).Error; err != nil {
		return nil, nil, nil, err
	}

	return &adminUser, &adminRole, permissions, nil
}

// CleanupTestDB 清理测试数据库
func CleanupTestDB(db *gorm.DB) {
	db.Exec("DELETE FROM user_roles")
	db.Exec("DELETE FROM role_permissions")
	db.Exec("DELETE FROM users")
	db.Exec("DELETE FROM roles")
	db.Exec("DELETE FROM permissions")
}

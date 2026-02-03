package routes

import (
	"rbac-golang/config"
	"rbac-golang/handlers"
	"rbac-golang/middleware"

	"github.com/gin-gonic/gin"
)

// SetupRouter 配置路由
func SetupRouter(cfg *config.Config) *gin.Engine {
	// 设置运行模式
	gin.SetMode(cfg.Server.Mode)

	router := gin.New()
	router.Use(gin.Recovery())
	router.Use(gin.Logger())
	router.Use(middleware.CORSMiddleware())

	// 创建处理器
	authHandler := handlers.NewAuthHandler(cfg)
	userHandler := handlers.NewUserHandler()
	roleHandler := handlers.NewRoleHandler()
	permissionHandler := handlers.NewPermissionHandler()

	// API v1 路由组
	v1 := router.Group("/api/v1")
	{
		// 公开接口（无需认证）
		v1.POST("/login", authHandler.Login)

		// 需要认证的接口
		auth := v1.Group("")
		auth.Use(middleware.AuthMiddleware(cfg))
		{
			// 当前用户相关
			auth.GET("/me", authHandler.GetCurrentUser)
			auth.PUT("/me/password", authHandler.ChangePassword)

			// 用户管理
			users := auth.Group("/users")
			{
				users.GET("", middleware.PermissionMiddleware("user:list"), userHandler.List)
				users.GET("/:id", middleware.PermissionMiddleware("user:list"), userHandler.Get)
				users.POST("", middleware.PermissionMiddleware("user:create"), userHandler.Create)
				users.PUT("/:id", middleware.PermissionMiddleware("user:update"), userHandler.Update)
				users.DELETE("/:id", middleware.PermissionMiddleware("user:delete"), userHandler.Delete)
				users.PUT("/:id/roles", middleware.PermissionMiddleware("user:update"), userHandler.AssignRoles)
				users.GET("/:id/roles", middleware.PermissionMiddleware("user:list"), userHandler.GetUserRoles)
				users.GET("/:id/permissions", middleware.PermissionMiddleware("user:list"), userHandler.GetUserPermissions)
				users.PUT("/:id/password", middleware.PermissionMiddleware("user:update"), userHandler.ResetPassword)
			}

			// 角色管理
			roles := auth.Group("/roles")
			{
				roles.GET("", middleware.PermissionMiddleware("role:list"), roleHandler.List)
				roles.GET("/all", middleware.PermissionMiddleware("role:list"), roleHandler.ListAll)
				roles.GET("/:id", middleware.PermissionMiddleware("role:list"), roleHandler.Get)
				roles.POST("", middleware.PermissionMiddleware("role:create"), roleHandler.Create)
				roles.PUT("/:id", middleware.PermissionMiddleware("role:update"), roleHandler.Update)
				roles.DELETE("/:id", middleware.PermissionMiddleware("role:delete"), roleHandler.Delete)
				roles.PUT("/:id/permissions", middleware.PermissionMiddleware("role:update"), roleHandler.AssignPermissions)
				roles.GET("/:id/permissions", middleware.PermissionMiddleware("role:list"), roleHandler.GetRolePermissions)
			}

			// 权限管理
			permissions := auth.Group("/permissions")
			{
				permissions.GET("", middleware.PermissionMiddleware("permission:list"), permissionHandler.List)
				permissions.GET("/all", middleware.PermissionMiddleware("permission:list"), permissionHandler.ListAll)
				permissions.GET("/tree", middleware.PermissionMiddleware("permission:list"), permissionHandler.Tree)
				permissions.GET("/:id", middleware.PermissionMiddleware("permission:list"), permissionHandler.Get)
				permissions.POST("", middleware.PermissionMiddleware("permission:create"), permissionHandler.Create)
				permissions.PUT("/:id", middleware.PermissionMiddleware("permission:update"), permissionHandler.Update)
				permissions.DELETE("/:id", middleware.PermissionMiddleware("permission:delete"), permissionHandler.Delete)
			}
		}
	}

	// 健康检查
	router.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	return router
}

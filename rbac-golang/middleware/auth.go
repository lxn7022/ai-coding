package middleware

import (
	"rbac-golang/config"
	"rbac-golang/database"
	"rbac-golang/handlers"
	"rbac-golang/models"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
)

// AuthMiddleware JWT认证中间件
func AuthMiddleware(cfg *config.Config) gin.HandlerFunc {
	return func(c *gin.Context) {
		// 获取Authorization头
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			handlers.Unauthorized(c, "请先登录")
			c.Abort()
			return
		}

		// 检查Bearer前缀
		parts := strings.SplitN(authHeader, " ", 2)
		if len(parts) != 2 || parts[0] != "Bearer" {
			handlers.Unauthorized(c, "Token格式错误")
			c.Abort()
			return
		}

		tokenString := parts[1]

		// 解析Token
		claims := &handlers.Claims{}
		token, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
			return []byte(cfg.JWT.Secret), nil
		})

		if err != nil || !token.Valid {
			handlers.Unauthorized(c, "Token无效或已过期")
			c.Abort()
			return
		}

		// 检查用户是否存在且状态正常
		var user models.User
		if err := database.DB.First(&user, claims.UserID).Error; err != nil {
			handlers.Unauthorized(c, "用户不存在")
			c.Abort()
			return
		}

		if user.Status != 1 {
			handlers.Forbidden(c, "用户已被禁用")
			c.Abort()
			return
		}

		// 将用户信息存入上下文
		c.Set("userID", claims.UserID)
		c.Set("username", claims.Username)

		c.Next()
	}
}

// PermissionMiddleware 权限检查中间件
func PermissionMiddleware(permissionCode string) gin.HandlerFunc {
	return func(c *gin.Context) {
		userID, exists := c.Get("userID")
		if !exists {
			handlers.Unauthorized(c, "未登录")
			c.Abort()
			return
		}

		// 获取用户及其角色和权限
		var user models.User
		if err := database.DB.Preload("Roles.Permissions").First(&user, userID).Error; err != nil {
			handlers.Unauthorized(c, "用户不存在")
			c.Abort()
			return
		}

		// 检查是否有超级管理员角色（admin角色拥有所有权限）
		for _, role := range user.Roles {
			if role.Code == "admin" {
				c.Next()
				return
			}
		}

		// 检查是否拥有指定权限
		if !user.HasPermission(permissionCode) {
			handlers.Forbidden(c, "没有操作权限")
			c.Abort()
			return
		}

		c.Next()
	}
}

// RoleMiddleware 角色检查中间件
func RoleMiddleware(roleCodes ...string) gin.HandlerFunc {
	return func(c *gin.Context) {
		userID, exists := c.Get("userID")
		if !exists {
			handlers.Unauthorized(c, "未登录")
			c.Abort()
			return
		}

		// 获取用户及其角色
		var user models.User
		if err := database.DB.Preload("Roles").First(&user, userID).Error; err != nil {
			handlers.Unauthorized(c, "用户不存在")
			c.Abort()
			return
		}

		// 检查是否拥有指定角色之一
		for _, roleCode := range roleCodes {
			if user.HasRole(roleCode) {
				c.Next()
				return
			}
		}

		handlers.Forbidden(c, "没有操作权限")
		c.Abort()
	}
}

// AdminMiddleware 管理员权限中间件
func AdminMiddleware() gin.HandlerFunc {
	return RoleMiddleware("admin")
}

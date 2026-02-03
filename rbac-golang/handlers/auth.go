package handlers

import (
	"rbac-golang/config"
	"rbac-golang/database"
	"rbac-golang/models"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
)

// AuthHandler 认证处理器
type AuthHandler struct {
	config *config.Config
}

// NewAuthHandler 创建认证处理器
func NewAuthHandler(cfg *config.Config) *AuthHandler {
	return &AuthHandler{config: cfg}
}

// Claims JWT声明
type Claims struct {
	UserID   uint   `json:"user_id"`
	Username string `json:"username"`
	jwt.RegisteredClaims
}

// Login 用户登录
func (h *AuthHandler) Login(c *gin.Context) {
	var req models.LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		BadRequest(c, "请求参数错误: "+err.Error())
		return
	}

	// 查找用户
	var user models.User
	if err := database.DB.Where("username = ?", req.Username).First(&user).Error; err != nil {
		Unauthorized(c, "用户名或密码错误")
		return
	}

	// 检查用户状态
	if user.Status != 1 {
		Forbidden(c, "用户已被禁用")
		return
	}

	// 验证密码
	if !user.CheckPassword(req.Password) {
		Unauthorized(c, "用户名或密码错误")
		return
	}

	// 生成JWT Token
	token, err := h.generateToken(&user)
	if err != nil {
		InternalError(c, "生成Token失败")
		return
	}

	// 预加载用户角色
	database.DB.Preload("Roles").First(&user, user.ID)

	Success(c, models.LoginResponse{
		Token: token,
		User:  user,
	})
}

// generateToken 生成JWT Token
func (h *AuthHandler) generateToken(user *models.User) (string, error) {
	claims := Claims{
		UserID:   user.ID,
		Username: user.Username,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(h.config.JWT.ExpireTime)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			Issuer:    "rbac-system",
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(h.config.JWT.Secret))
}

// GetCurrentUser 获取当前登录用户信息
func (h *AuthHandler) GetCurrentUser(c *gin.Context) {
	userID, exists := c.Get("userID")
	if !exists {
		Unauthorized(c, "未登录")
		return
	}

	var user models.User
	if err := database.DB.Preload("Roles.Permissions").First(&user, userID).Error; err != nil {
		NotFound(c, "用户不存在")
		return
	}

	Success(c, user)
}

// ChangePassword 修改密码
func (h *AuthHandler) ChangePassword(c *gin.Context) {
	type ChangePasswordRequest struct {
		OldPassword string `json:"old_password" binding:"required"`
		NewPassword string `json:"new_password" binding:"required,min=6,max=50"`
	}

	var req ChangePasswordRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		BadRequest(c, "请求参数错误: "+err.Error())
		return
	}

	userID, _ := c.Get("userID")
	var user models.User
	if err := database.DB.First(&user, userID).Error; err != nil {
		NotFound(c, "用户不存在")
		return
	}

	// 验证旧密码
	if !user.CheckPassword(req.OldPassword) {
		BadRequest(c, "原密码错误")
		return
	}

	// 设置新密码
	if err := user.SetPassword(req.NewPassword); err != nil {
		InternalError(c, "密码加密失败")
		return
	}

	if err := database.DB.Save(&user).Error; err != nil {
		InternalError(c, "保存失败")
		return
	}

	SuccessWithMessage(c, "密码修改成功", nil)
}

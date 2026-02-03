package handlers

import (
	"rbac-golang/database"
	"rbac-golang/models"
	"strconv"

	"github.com/gin-gonic/gin"
)

// UserHandler 用户处理器
type UserHandler struct{}

// NewUserHandler 创建用户处理器
func NewUserHandler() *UserHandler {
	return &UserHandler{}
}

// List 获取用户列表
func (h *UserHandler) List(c *gin.Context) {
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	pageSize, _ := strconv.Atoi(c.DefaultQuery("page_size", "10"))
	username := c.Query("username")
	status := c.Query("status")

	if page < 1 {
		page = 1
	}
	if pageSize < 1 || pageSize > 100 {
		pageSize = 10
	}

	var users []models.User
	var total int64

	query := database.DB.Model(&models.User{})

	if username != "" {
		query = query.Where("username LIKE ?", "%"+username+"%")
	}
	if status != "" {
		query = query.Where("status = ?", status)
	}

	query.Count(&total)
	query.Preload("Roles").Offset((page - 1) * pageSize).Limit(pageSize).Find(&users)

	SuccessPage(c, users, total, page, pageSize)
}

// Get 获取单个用户
func (h *UserHandler) Get(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		BadRequest(c, "无效的用户ID")
		return
	}

	var user models.User
	if err := database.DB.Preload("Roles.Permissions").First(&user, id).Error; err != nil {
		NotFound(c, "用户不存在")
		return
	}

	Success(c, user)
}

// Create 创建用户
func (h *UserHandler) Create(c *gin.Context) {
	var req models.CreateUserRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		BadRequest(c, "请求参数错误: "+err.Error())
		return
	}

	// 检查用户名是否已存在
	var count int64
	database.DB.Model(&models.User{}).Where("username = ?", req.Username).Count(&count)
	if count > 0 {
		BadRequest(c, "用户名已存在")
		return
	}

	// 检查邮箱是否已存在
	if req.Email != "" {
		database.DB.Model(&models.User{}).Where("email = ?", req.Email).Count(&count)
		if count > 0 {
			BadRequest(c, "邮箱已存在")
			return
		}
	}

	user := models.User{
		Username: req.Username,
		Password: req.Password,
		Email:    req.Email,
		Nickname: req.Nickname,
	}

	if err := database.DB.Create(&user).Error; err != nil {
		InternalError(c, "创建用户失败")
		return
	}

	Success(c, user)
}

// Update 更新用户
func (h *UserHandler) Update(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		BadRequest(c, "无效的用户ID")
		return
	}

	var user models.User
	if err := database.DB.First(&user, id).Error; err != nil {
		NotFound(c, "用户不存在")
		return
	}

	var req models.UpdateUserRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		BadRequest(c, "请求参数错误: "+err.Error())
		return
	}

	// 检查邮箱是否已被其他用户使用
	if req.Email != "" && req.Email != user.Email {
		var count int64
		database.DB.Model(&models.User{}).Where("email = ? AND id != ?", req.Email, id).Count(&count)
		if count > 0 {
			BadRequest(c, "邮箱已存在")
			return
		}
		user.Email = req.Email
	}

	if req.Nickname != "" {
		user.Nickname = req.Nickname
	}
	if req.Status != nil {
		user.Status = *req.Status
	}

	if err := database.DB.Save(&user).Error; err != nil {
		InternalError(c, "更新用户失败")
		return
	}

	Success(c, user)
}

// Delete 删除用户
func (h *UserHandler) Delete(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		BadRequest(c, "无效的用户ID")
		return
	}

	var user models.User
	if err := database.DB.First(&user, id).Error; err != nil {
		NotFound(c, "用户不存在")
		return
	}

	// 禁止删除admin用户
	if user.Username == "admin" {
		Forbidden(c, "不能删除管理员账号")
		return
	}

	// 删除用户的角色关联
	database.DB.Model(&user).Association("Roles").Clear()

	// 删除用户
	if err := database.DB.Delete(&user).Error; err != nil {
		InternalError(c, "删除用户失败")
		return
	}

	SuccessWithMessage(c, "删除成功", nil)
}

// AssignRoles 给用户分配角色
func (h *UserHandler) AssignRoles(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		BadRequest(c, "无效的用户ID")
		return
	}

	var user models.User
	if err := database.DB.First(&user, id).Error; err != nil {
		NotFound(c, "用户不存在")
		return
	}

	var req models.AssignRolesRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		BadRequest(c, "请求参数错误: "+err.Error())
		return
	}

	// 获取要分配的角色
	var roles []models.Role
	if err := database.DB.Where("id IN ?", req.RoleIDs).Find(&roles).Error; err != nil {
		InternalError(c, "查询角色失败")
		return
	}

	// 替换用户的角色
	if err := database.DB.Model(&user).Association("Roles").Replace(roles); err != nil {
		InternalError(c, "分配角色失败")
		return
	}

	// 重新加载用户信息
	database.DB.Preload("Roles").First(&user, id)

	Success(c, user)
}

// GetUserRoles 获取用户的角色列表
func (h *UserHandler) GetUserRoles(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		BadRequest(c, "无效的用户ID")
		return
	}

	var user models.User
	if err := database.DB.Preload("Roles").First(&user, id).Error; err != nil {
		NotFound(c, "用户不存在")
		return
	}

	Success(c, user.Roles)
}

// GetUserPermissions 获取用户的权限列表
func (h *UserHandler) GetUserPermissions(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		BadRequest(c, "无效的用户ID")
		return
	}

	var user models.User
	if err := database.DB.Preload("Roles.Permissions").First(&user, id).Error; err != nil {
		NotFound(c, "用户不存在")
		return
	}

	// 合并所有角色的权限并去重
	permissionMap := make(map[uint]models.Permission)
	for _, role := range user.Roles {
		for _, perm := range role.Permissions {
			permissionMap[perm.ID] = perm
		}
	}

	permissions := make([]models.Permission, 0, len(permissionMap))
	for _, perm := range permissionMap {
		permissions = append(permissions, perm)
	}

	Success(c, permissions)
}

// ResetPassword 重置用户密码
func (h *UserHandler) ResetPassword(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		BadRequest(c, "无效的用户ID")
		return
	}

	type ResetPasswordRequest struct {
		NewPassword string `json:"new_password" binding:"required,min=6,max=50"`
	}

	var req ResetPasswordRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		BadRequest(c, "请求参数错误: "+err.Error())
		return
	}

	var user models.User
	if err := database.DB.First(&user, id).Error; err != nil {
		NotFound(c, "用户不存在")
		return
	}

	if err := user.SetPassword(req.NewPassword); err != nil {
		InternalError(c, "密码加密失败")
		return
	}

	if err := database.DB.Save(&user).Error; err != nil {
		InternalError(c, "保存失败")
		return
	}

	SuccessWithMessage(c, "密码重置成功", nil)
}

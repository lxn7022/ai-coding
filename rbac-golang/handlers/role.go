package handlers

import (
	"rbac-golang/database"
	"rbac-golang/models"
	"strconv"

	"github.com/gin-gonic/gin"
)

// RoleHandler 角色处理器
type RoleHandler struct{}

// NewRoleHandler 创建角色处理器
func NewRoleHandler() *RoleHandler {
	return &RoleHandler{}
}

// List 获取角色列表
func (h *RoleHandler) List(c *gin.Context) {
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	pageSize, _ := strconv.Atoi(c.DefaultQuery("page_size", "10"))
	name := c.Query("name")
	status := c.Query("status")

	if page < 1 {
		page = 1
	}
	if pageSize < 1 || pageSize > 100 {
		pageSize = 10
	}

	var roles []models.Role
	var total int64

	query := database.DB.Model(&models.Role{})

	if name != "" {
		query = query.Where("name LIKE ?", "%"+name+"%")
	}
	if status != "" {
		query = query.Where("status = ?", status)
	}

	query.Count(&total)
	query.Preload("Permissions").Offset((page - 1) * pageSize).Limit(pageSize).Find(&roles)

	SuccessPage(c, roles, total, page, pageSize)
}

// ListAll 获取所有角色（不分页）
func (h *RoleHandler) ListAll(c *gin.Context) {
	var roles []models.Role
	database.DB.Where("status = ?", 1).Find(&roles)
	Success(c, roles)
}

// Get 获取单个角色
func (h *RoleHandler) Get(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		BadRequest(c, "无效的角色ID")
		return
	}

	var role models.Role
	if err := database.DB.Preload("Permissions").First(&role, id).Error; err != nil {
		NotFound(c, "角色不存在")
		return
	}

	Success(c, role)
}

// Create 创建角色
func (h *RoleHandler) Create(c *gin.Context) {
	var req models.CreateRoleRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		BadRequest(c, "请求参数错误: "+err.Error())
		return
	}

	// 检查角色编码是否已存在
	var count int64
	database.DB.Model(&models.Role{}).Where("code = ?", req.Code).Count(&count)
	if count > 0 {
		BadRequest(c, "角色编码已存在")
		return
	}

	role := models.Role{
		Name:        req.Name,
		Code:        req.Code,
		Description: req.Description,
	}

	if err := database.DB.Create(&role).Error; err != nil {
		InternalError(c, "创建角色失败")
		return
	}

	Success(c, role)
}

// Update 更新角色
func (h *RoleHandler) Update(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		BadRequest(c, "无效的角色ID")
		return
	}

	var role models.Role
	if err := database.DB.First(&role, id).Error; err != nil {
		NotFound(c, "角色不存在")
		return
	}

	var req models.UpdateRoleRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		BadRequest(c, "请求参数错误: "+err.Error())
		return
	}

	if req.Name != "" {
		role.Name = req.Name
	}
	if req.Description != "" {
		role.Description = req.Description
	}
	if req.Status != nil {
		role.Status = *req.Status
	}

	if err := database.DB.Save(&role).Error; err != nil {
		InternalError(c, "更新角色失败")
		return
	}

	Success(c, role)
}

// Delete 删除角色
func (h *RoleHandler) Delete(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		BadRequest(c, "无效的角色ID")
		return
	}

	var role models.Role
	if err := database.DB.First(&role, id).Error; err != nil {
		NotFound(c, "角色不存在")
		return
	}

	// 禁止删除admin角色
	if role.Code == "admin" {
		Forbidden(c, "不能删除管理员角色")
		return
	}

	// 检查是否有用户使用该角色
	var userCount int64
	database.DB.Model(&role).Association("Users").Count()
	if userCount > 0 {
		BadRequest(c, "该角色下还有用户，无法删除")
		return
	}

	// 删除角色的权限关联
	database.DB.Model(&role).Association("Permissions").Clear()

	// 删除角色
	if err := database.DB.Delete(&role).Error; err != nil {
		InternalError(c, "删除角色失败")
		return
	}

	SuccessWithMessage(c, "删除成功", nil)
}

// AssignPermissions 给角色分配权限
func (h *RoleHandler) AssignPermissions(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		BadRequest(c, "无效的角色ID")
		return
	}

	var role models.Role
	if err := database.DB.First(&role, id).Error; err != nil {
		NotFound(c, "角色不存在")
		return
	}

	var req models.AssignPermissionsRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		BadRequest(c, "请求参数错误: "+err.Error())
		return
	}

	// 获取要分配的权限
	var permissions []models.Permission
	if err := database.DB.Where("id IN ?", req.PermissionIDs).Find(&permissions).Error; err != nil {
		InternalError(c, "查询权限失败")
		return
	}

	// 替换角色的权限
	if err := database.DB.Model(&role).Association("Permissions").Replace(permissions); err != nil {
		InternalError(c, "分配权限失败")
		return
	}

	// 重新加载角色信息
	database.DB.Preload("Permissions").First(&role, id)

	Success(c, role)
}

// GetRolePermissions 获取角色的权限列表
func (h *RoleHandler) GetRolePermissions(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		BadRequest(c, "无效的角色ID")
		return
	}

	var role models.Role
	if err := database.DB.Preload("Permissions").First(&role, id).Error; err != nil {
		NotFound(c, "角色不存在")
		return
	}

	Success(c, role.Permissions)
}

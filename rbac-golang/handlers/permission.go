package handlers

import (
	"rbac-golang/database"
	"rbac-golang/models"
	"strconv"

	"github.com/gin-gonic/gin"
)

// PermissionHandler 权限处理器
type PermissionHandler struct{}

// NewPermissionHandler 创建权限处理器
func NewPermissionHandler() *PermissionHandler {
	return &PermissionHandler{}
}

// List 获取权限列表
func (h *PermissionHandler) List(c *gin.Context) {
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	pageSize, _ := strconv.Atoi(c.DefaultQuery("page_size", "10"))
	name := c.Query("name")
	permType := c.Query("type")
	status := c.Query("status")

	if page < 1 {
		page = 1
	}
	if pageSize < 1 || pageSize > 100 {
		pageSize = 10
	}

	var permissions []models.Permission
	var total int64

	query := database.DB.Model(&models.Permission{})

	if name != "" {
		query = query.Where("name LIKE ?", "%"+name+"%")
	}
	if permType != "" {
		query = query.Where("type = ?", permType)
	}
	if status != "" {
		query = query.Where("status = ?", status)
	}

	query.Count(&total)
	query.Order("sort ASC, id ASC").Offset((page - 1) * pageSize).Limit(pageSize).Find(&permissions)

	SuccessPage(c, permissions, total, page, pageSize)
}

// ListAll 获取所有权限（不分页）
func (h *PermissionHandler) ListAll(c *gin.Context) {
	var permissions []models.Permission
	database.DB.Where("status = ?", 1).Order("sort ASC, id ASC").Find(&permissions)
	Success(c, permissions)
}

// Tree 获取权限树
func (h *PermissionHandler) Tree(c *gin.Context) {
	var permissions []models.Permission
	database.DB.Where("status = ?", 1).Order("sort ASC, id ASC").Find(&permissions)

	// 构建权限树
	tree := buildPermissionTree(permissions, nil)
	Success(c, tree)
}

// buildPermissionTree 构建权限树
func buildPermissionTree(permissions []models.Permission, parentID *uint) []models.PermissionTree {
	var tree []models.PermissionTree

	for _, perm := range permissions {
		// 比较parent_id
		if (perm.ParentID == nil && parentID == nil) ||
			(perm.ParentID != nil && parentID != nil && *perm.ParentID == *parentID) {
			node := models.PermissionTree{
				Permission: perm,
				Children:   buildPermissionTree(permissions, &perm.ID),
			}
			tree = append(tree, node)
		}
	}

	return tree
}

// Get 获取单个权限
func (h *PermissionHandler) Get(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		BadRequest(c, "无效的权限ID")
		return
	}

	var permission models.Permission
	if err := database.DB.First(&permission, id).Error; err != nil {
		NotFound(c, "权限不存在")
		return
	}

	Success(c, permission)
}

// Create 创建权限
func (h *PermissionHandler) Create(c *gin.Context) {
	var req models.CreatePermissionRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		BadRequest(c, "请求参数错误: "+err.Error())
		return
	}

	// 检查权限编码是否已存在
	var count int64
	database.DB.Model(&models.Permission{}).Where("code = ?", req.Code).Count(&count)
	if count > 0 {
		BadRequest(c, "权限编码已存在")
		return
	}

	// 如果指定了父级ID，检查父级是否存在
	if req.ParentID != nil {
		var parentCount int64
		database.DB.Model(&models.Permission{}).Where("id = ?", *req.ParentID).Count(&parentCount)
		if parentCount == 0 {
			BadRequest(c, "父级权限不存在")
			return
		}
	}

	permission := models.Permission{
		Name:        req.Name,
		Code:        req.Code,
		Type:        req.Type,
		Path:        req.Path,
		Method:      req.Method,
		ParentID:    req.ParentID,
		Description: req.Description,
		Sort:        req.Sort,
	}

	if err := database.DB.Create(&permission).Error; err != nil {
		InternalError(c, "创建权限失败")
		return
	}

	Success(c, permission)
}

// Update 更新权限
func (h *PermissionHandler) Update(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		BadRequest(c, "无效的权限ID")
		return
	}

	var permission models.Permission
	if err := database.DB.First(&permission, id).Error; err != nil {
		NotFound(c, "权限不存在")
		return
	}

	var req models.UpdatePermissionRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		BadRequest(c, "请求参数错误: "+err.Error())
		return
	}

	// 如果指定了父级ID，检查父级是否存在且不是自己
	if req.ParentID != nil {
		if *req.ParentID == uint(id) {
			BadRequest(c, "不能将自己设为父级")
			return
		}
		var parentCount int64
		database.DB.Model(&models.Permission{}).Where("id = ?", *req.ParentID).Count(&parentCount)
		if parentCount == 0 {
			BadRequest(c, "父级权限不存在")
			return
		}
		permission.ParentID = req.ParentID
	}

	if req.Name != "" {
		permission.Name = req.Name
	}
	if req.Path != "" {
		permission.Path = req.Path
	}
	if req.Method != "" {
		permission.Method = req.Method
	}
	if req.Description != "" {
		permission.Description = req.Description
	}
	if req.Status != nil {
		permission.Status = *req.Status
	}
	if req.Sort != nil {
		permission.Sort = *req.Sort
	}

	if err := database.DB.Save(&permission).Error; err != nil {
		InternalError(c, "更新权限失败")
		return
	}

	Success(c, permission)
}

// Delete 删除权限
func (h *PermissionHandler) Delete(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		BadRequest(c, "无效的权限ID")
		return
	}

	var permission models.Permission
	if err := database.DB.First(&permission, id).Error; err != nil {
		NotFound(c, "权限不存在")
		return
	}

	// 检查是否有子权限
	var childCount int64
	database.DB.Model(&models.Permission{}).Where("parent_id = ?", id).Count(&childCount)
	if childCount > 0 {
		BadRequest(c, "该权限下还有子权限，无法删除")
		return
	}

	// 删除权限（会自动清除关联）
	if err := database.DB.Delete(&permission).Error; err != nil {
		InternalError(c, "删除权限失败")
		return
	}

	SuccessWithMessage(c, "删除成功", nil)
}

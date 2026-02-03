package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"rbac-golang/database"
	"rbac-golang/models"

	"github.com/gin-gonic/gin"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

func setupPermissionTestDB(t *testing.T) *gorm.DB {
	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Silent),
	})
	if err != nil {
		t.Fatalf("Failed to connect to test database: %v", err)
	}

	err = db.AutoMigrate(&models.User{}, &models.Role{}, &models.Permission{})
	if err != nil {
		t.Fatalf("Failed to migrate: %v", err)
	}

	database.DB = db
	return db
}

func TestPermissionHandler_List(t *testing.T) {
	db := setupPermissionTestDB(t)
	gin.SetMode(gin.TestMode)

	perms := []models.Permission{
		{Name: "Perm1", Code: "perm1", Type: "api", Status: 1},
		{Name: "Perm2", Code: "perm2", Type: "menu", Status: 1},
		{Name: "Perm3", Code: "perm3", Type: "button", Status: 0},
	}
	for _, p := range perms {
		db.Create(&p)
	}

	handler := NewPermissionHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("GET", "/api/v1/permissions?page=1&page_size=10", nil)

	handler.List(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}

	var resp Response
	json.Unmarshal(w.Body.Bytes(), &resp)

	if resp.Code != 0 {
		t.Errorf("Expected code 0, got %d", resp.Code)
	}
}

func TestPermissionHandler_List_WithFilter(t *testing.T) {
	db := setupPermissionTestDB(t)
	gin.SetMode(gin.TestMode)

	perms := []models.Permission{
		{Name: "API Perm", Code: "api:perm", Type: "api", Status: 1},
		{Name: "Menu Perm", Code: "menu:perm", Type: "menu", Status: 1},
	}
	for _, p := range perms {
		db.Create(&p)
	}

	handler := NewPermissionHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("GET", "/api/v1/permissions?name=API&type=api&status=1", nil)

	handler.List(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestPermissionHandler_ListAll(t *testing.T) {
	db := setupPermissionTestDB(t)
	gin.SetMode(gin.TestMode)

	perms := []models.Permission{
		{Name: "Enabled", Code: "enabled", Type: "api", Status: 1},
		{Name: "Disabled", Code: "disabled", Type: "api", Status: 0},
	}
	for _, p := range perms {
		db.Create(&p)
	}

	handler := NewPermissionHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("GET", "/api/v1/permissions/all", nil)

	handler.ListAll(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestPermissionHandler_Tree(t *testing.T) {
	db := setupPermissionTestDB(t)
	gin.SetMode(gin.TestMode)

	// 创建层级权限
	parent := models.Permission{Name: "Parent", Code: "parent", Type: "menu", Status: 1}
	db.Create(&parent)

	child := models.Permission{Name: "Child", Code: "child", Type: "api", Status: 1, ParentID: &parent.ID}
	db.Create(&child)

	handler := NewPermissionHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("GET", "/api/v1/permissions/tree", nil)

	handler.Tree(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestPermissionHandler_Get_Success(t *testing.T) {
	db := setupPermissionTestDB(t)
	gin.SetMode(gin.TestMode)

	perm := models.Permission{Name: "Test", Code: "test", Type: "api"}
	db.Create(&perm)

	handler := NewPermissionHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("GET", "/api/v1/permissions/1", nil)
	c.Params = gin.Params{{Key: "id", Value: "1"}}

	handler.Get(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestPermissionHandler_Get_NotFound(t *testing.T) {
	setupPermissionTestDB(t)
	gin.SetMode(gin.TestMode)

	handler := NewPermissionHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("GET", "/api/v1/permissions/999", nil)
	c.Params = gin.Params{{Key: "id", Value: "999"}}

	handler.Get(c)

	if w.Code != http.StatusNotFound {
		t.Errorf("Expected status %d, got %d", http.StatusNotFound, w.Code)
	}
}

func TestPermissionHandler_Create_Success(t *testing.T) {
	setupPermissionTestDB(t)
	gin.SetMode(gin.TestMode)

	handler := NewPermissionHandler()

	req := models.CreatePermissionRequest{
		Name:        "New Permission",
		Code:        "new:perm",
		Type:        "api",
		Path:        "/api/test",
		Method:      "GET",
		Description: "A new permission",
	}
	body, _ := json.Marshal(req)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("POST", "/api/v1/permissions", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")

	handler.Create(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestPermissionHandler_Create_DuplicateCode(t *testing.T) {
	db := setupPermissionTestDB(t)
	gin.SetMode(gin.TestMode)

	existingPerm := models.Permission{Name: "Existing", Code: "existing:perm", Type: "api"}
	db.Create(&existingPerm)

	handler := NewPermissionHandler()

	req := models.CreatePermissionRequest{
		Name: "New Permission",
		Code: "existing:perm", // 重复的编码
		Type: "api",
	}
	body, _ := json.Marshal(req)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("POST", "/api/v1/permissions", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")

	handler.Create(c)

	if w.Code != http.StatusBadRequest {
		t.Errorf("Expected status %d, got %d", http.StatusBadRequest, w.Code)
	}
}

func TestPermissionHandler_Create_WithParent(t *testing.T) {
	db := setupPermissionTestDB(t)
	gin.SetMode(gin.TestMode)

	parent := models.Permission{Name: "Parent", Code: "parent", Type: "menu"}
	db.Create(&parent)

	handler := NewPermissionHandler()

	parentID := parent.ID
	req := models.CreatePermissionRequest{
		Name:     "Child Permission",
		Code:     "child:perm",
		Type:     "api",
		ParentID: &parentID,
	}
	body, _ := json.Marshal(req)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("POST", "/api/v1/permissions", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")

	handler.Create(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestPermissionHandler_Create_InvalidParent(t *testing.T) {
	setupPermissionTestDB(t)
	gin.SetMode(gin.TestMode)

	handler := NewPermissionHandler()

	parentID := uint(999) // 不存在的父级
	req := models.CreatePermissionRequest{
		Name:     "Child Permission",
		Code:     "child:perm",
		Type:     "api",
		ParentID: &parentID,
	}
	body, _ := json.Marshal(req)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("POST", "/api/v1/permissions", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")

	handler.Create(c)

	if w.Code != http.StatusBadRequest {
		t.Errorf("Expected status %d, got %d", http.StatusBadRequest, w.Code)
	}
}

func TestPermissionHandler_Update_Success(t *testing.T) {
	db := setupPermissionTestDB(t)
	gin.SetMode(gin.TestMode)

	perm := models.Permission{Name: "Test", Code: "test", Type: "api", Status: 1}
	db.Create(&perm)

	handler := NewPermissionHandler()

	status := 0
	req := models.UpdatePermissionRequest{
		Name:   "Updated Test",
		Status: &status,
	}
	body, _ := json.Marshal(req)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("PUT", "/api/v1/permissions/1", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")
	c.Params = gin.Params{{Key: "id", Value: "1"}}

	handler.Update(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestPermissionHandler_Update_SelfAsParent(t *testing.T) {
	db := setupPermissionTestDB(t)
	gin.SetMode(gin.TestMode)

	perm := models.Permission{Name: "Test", Code: "test", Type: "api"}
	db.Create(&perm)

	handler := NewPermissionHandler()

	parentID := perm.ID // 自己作为父级
	req := models.UpdatePermissionRequest{
		ParentID: &parentID,
	}
	body, _ := json.Marshal(req)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("PUT", "/api/v1/permissions/1", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")
	c.Params = gin.Params{{Key: "id", Value: "1"}}

	handler.Update(c)

	if w.Code != http.StatusBadRequest {
		t.Errorf("Expected status %d, got %d", http.StatusBadRequest, w.Code)
	}
}

func TestPermissionHandler_Delete_Success(t *testing.T) {
	db := setupPermissionTestDB(t)
	gin.SetMode(gin.TestMode)

	perm := models.Permission{Name: "Test", Code: "test", Type: "api"}
	db.Create(&perm)

	handler := NewPermissionHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("DELETE", "/api/v1/permissions/1", nil)
	c.Params = gin.Params{{Key: "id", Value: "1"}}

	handler.Delete(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestPermissionHandler_Delete_HasChildren(t *testing.T) {
	db := setupPermissionTestDB(t)
	gin.SetMode(gin.TestMode)

	parent := models.Permission{Name: "Parent", Code: "parent", Type: "menu"}
	db.Create(&parent)

	child := models.Permission{Name: "Child", Code: "child", Type: "api", ParentID: &parent.ID}
	db.Create(&child)

	handler := NewPermissionHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("DELETE", "/api/v1/permissions/1", nil)
	c.Params = gin.Params{{Key: "id", Value: "1"}}

	handler.Delete(c)

	if w.Code != http.StatusBadRequest {
		t.Errorf("Expected status %d, got %d", http.StatusBadRequest, w.Code)
	}
}

func TestPermissionHandler_InvalidID(t *testing.T) {
	setupPermissionTestDB(t)
	gin.SetMode(gin.TestMode)

	handler := NewPermissionHandler()

	tests := []struct {
		name   string
		method string
		path   string
		action func(*gin.Context)
	}{
		{"Get", "GET", "/api/v1/permissions/invalid", handler.Get},
		{"Update", "PUT", "/api/v1/permissions/invalid", handler.Update},
		{"Delete", "DELETE", "/api/v1/permissions/invalid", handler.Delete},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			w := httptest.NewRecorder()
			c, _ := gin.CreateTestContext(w)
			c.Request, _ = http.NewRequest(tt.method, tt.path, nil)
			c.Params = gin.Params{{Key: "id", Value: "invalid"}}

			tt.action(c)

			if w.Code != http.StatusBadRequest {
				t.Errorf("Expected status %d, got %d", http.StatusBadRequest, w.Code)
			}
		})
	}
}

func TestNewPermissionHandler(t *testing.T) {
	handler := NewPermissionHandler()
	if handler == nil {
		t.Error("NewPermissionHandler() should not return nil")
	}
}

func TestBuildPermissionTree(t *testing.T) {
	permissions := []models.Permission{
		{Name: "Root1", Code: "root1", Type: "menu", ParentID: nil},
		{Name: "Root2", Code: "root2", Type: "menu", ParentID: nil},
	}
	permissions[0].ID = 1
	permissions[1].ID = 2

	parentID := uint(1)
	child := models.Permission{Name: "Child", Code: "child", Type: "api", ParentID: &parentID}
	child.ID = 3
	permissions = append(permissions, child)

	tree := buildPermissionTree(permissions, nil)

	if len(tree) != 2 {
		t.Errorf("Expected 2 root nodes, got %d", len(tree))
	}

	// 检查第一个节点的子节点
	if len(tree[0].Children) != 1 {
		t.Errorf("Expected 1 child for root1, got %d", len(tree[0].Children))
	}
}

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

func setupRoleTestDB(t *testing.T) *gorm.DB {
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

func TestRoleHandler_List(t *testing.T) {
	db := setupRoleTestDB(t)
	gin.SetMode(gin.TestMode)

	roles := []models.Role{
		{Name: "Admin", Code: "admin", Status: 1},
		{Name: "User", Code: "user", Status: 1},
		{Name: "Guest", Code: "guest", Status: 0},
	}
	for _, r := range roles {
		db.Create(&r)
	}

	handler := NewRoleHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("GET", "/api/v1/roles?page=1&page_size=10", nil)

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

func TestRoleHandler_List_WithFilter(t *testing.T) {
	db := setupRoleTestDB(t)
	gin.SetMode(gin.TestMode)

	roles := []models.Role{
		{Name: "Admin", Code: "admin", Status: 1},
		{Name: "User", Code: "user", Status: 1},
	}
	for _, r := range roles {
		db.Create(&r)
	}

	handler := NewRoleHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("GET", "/api/v1/roles?name=Admin&status=1", nil)

	handler.List(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestRoleHandler_ListAll(t *testing.T) {
	db := setupRoleTestDB(t)
	gin.SetMode(gin.TestMode)

	roles := []models.Role{
		{Name: "Admin", Code: "admin", Status: 1},
		{Name: "Disabled", Code: "disabled", Status: 0},
	}
	for _, r := range roles {
		db.Create(&r)
	}

	handler := NewRoleHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("GET", "/api/v1/roles/all", nil)

	handler.ListAll(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestRoleHandler_Get_Success(t *testing.T) {
	db := setupRoleTestDB(t)
	gin.SetMode(gin.TestMode)

	role := models.Role{Name: "Admin", Code: "admin"}
	db.Create(&role)

	handler := NewRoleHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("GET", "/api/v1/roles/1", nil)
	c.Params = gin.Params{{Key: "id", Value: "1"}}

	handler.Get(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestRoleHandler_Get_NotFound(t *testing.T) {
	setupRoleTestDB(t)
	gin.SetMode(gin.TestMode)

	handler := NewRoleHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("GET", "/api/v1/roles/999", nil)
	c.Params = gin.Params{{Key: "id", Value: "999"}}

	handler.Get(c)

	if w.Code != http.StatusNotFound {
		t.Errorf("Expected status %d, got %d", http.StatusNotFound, w.Code)
	}
}

func TestRoleHandler_Create_Success(t *testing.T) {
	setupRoleTestDB(t)
	gin.SetMode(gin.TestMode)

	handler := NewRoleHandler()

	req := models.CreateRoleRequest{
		Name:        "New Role",
		Code:        "new_role",
		Description: "A new role",
	}
	body, _ := json.Marshal(req)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("POST", "/api/v1/roles", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")

	handler.Create(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestRoleHandler_Create_DuplicateCode(t *testing.T) {
	db := setupRoleTestDB(t)
	gin.SetMode(gin.TestMode)

	existingRole := models.Role{Name: "Existing", Code: "existing_role"}
	db.Create(&existingRole)

	handler := NewRoleHandler()

	req := models.CreateRoleRequest{
		Name: "New Role",
		Code: "existing_role", // 重复的编码
	}
	body, _ := json.Marshal(req)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("POST", "/api/v1/roles", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")

	handler.Create(c)

	if w.Code != http.StatusBadRequest {
		t.Errorf("Expected status %d, got %d", http.StatusBadRequest, w.Code)
	}
}

func TestRoleHandler_Update_Success(t *testing.T) {
	db := setupRoleTestDB(t)
	gin.SetMode(gin.TestMode)

	role := models.Role{Name: "Admin", Code: "admin", Status: 1}
	db.Create(&role)

	handler := NewRoleHandler()

	status := 0
	req := models.UpdateRoleRequest{
		Name:   "Updated Admin",
		Status: &status,
	}
	body, _ := json.Marshal(req)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("PUT", "/api/v1/roles/1", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")
	c.Params = gin.Params{{Key: "id", Value: "1"}}

	handler.Update(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestRoleHandler_Delete_Success(t *testing.T) {
	db := setupRoleTestDB(t)
	gin.SetMode(gin.TestMode)

	role := models.Role{Name: "TestRole", Code: "test_role"}
	db.Create(&role)

	handler := NewRoleHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("DELETE", "/api/v1/roles/1", nil)
	c.Params = gin.Params{{Key: "id", Value: "1"}}

	handler.Delete(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestRoleHandler_Delete_AdminProtection(t *testing.T) {
	db := setupRoleTestDB(t)
	gin.SetMode(gin.TestMode)

	// 创建admin角色
	adminRole := models.Role{Name: "Admin", Code: "admin"}
	db.Create(&adminRole)

	handler := NewRoleHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("DELETE", "/api/v1/roles/1", nil)
	c.Params = gin.Params{{Key: "id", Value: "1"}}

	handler.Delete(c)

	if w.Code != http.StatusForbidden {
		t.Errorf("Expected status %d, got %d", http.StatusForbidden, w.Code)
	}
}

func TestRoleHandler_AssignPermissions_Success(t *testing.T) {
	db := setupRoleTestDB(t)
	gin.SetMode(gin.TestMode)

	role := models.Role{Name: "TestRole", Code: "test_role"}
	db.Create(&role)

	perm := models.Permission{Name: "Test Perm", Code: "test:perm", Type: "api"}
	db.Create(&perm)

	handler := NewRoleHandler()

	req := models.AssignPermissionsRequest{
		PermissionIDs: []uint{perm.ID},
	}
	body, _ := json.Marshal(req)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("PUT", "/api/v1/roles/1/permissions", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")
	c.Params = gin.Params{{Key: "id", Value: "1"}}

	handler.AssignPermissions(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestRoleHandler_GetRolePermissions(t *testing.T) {
	db := setupRoleTestDB(t)
	gin.SetMode(gin.TestMode)

	perm := models.Permission{Name: "Test Perm", Code: "test:perm", Type: "api"}
	db.Create(&perm)

	role := models.Role{Name: "TestRole", Code: "test_role", Permissions: []models.Permission{perm}}
	db.Create(&role)

	handler := NewRoleHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("GET", "/api/v1/roles/1/permissions", nil)
	c.Params = gin.Params{{Key: "id", Value: "1"}}

	handler.GetRolePermissions(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestRoleHandler_InvalidID(t *testing.T) {
	setupRoleTestDB(t)
	gin.SetMode(gin.TestMode)

	handler := NewRoleHandler()

	tests := []struct {
		name   string
		method string
		path   string
		action func(*gin.Context)
	}{
		{"Get", "GET", "/api/v1/roles/invalid", handler.Get},
		{"Update", "PUT", "/api/v1/roles/invalid", handler.Update},
		{"Delete", "DELETE", "/api/v1/roles/invalid", handler.Delete},
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

func TestNewRoleHandler(t *testing.T) {
	handler := NewRoleHandler()
	if handler == nil {
		t.Error("NewRoleHandler() should not return nil")
	}
}

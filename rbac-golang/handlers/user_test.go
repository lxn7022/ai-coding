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

func setupUserTestDB(t *testing.T) *gorm.DB {
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

func TestUserHandler_List(t *testing.T) {
	db := setupUserTestDB(t)
	gin.SetMode(gin.TestMode)

	// 创建测试数据
	users := []models.User{
		{Username: "user1", Password: "pass1", Email: "user1@test.com", Status: 1},
		{Username: "user2", Password: "pass2", Email: "user2@test.com", Status: 1},
		{Username: "user3", Password: "pass3", Email: "user3@test.com", Status: 0},
	}
	for _, u := range users {
		db.Create(&u)
	}

	handler := NewUserHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("GET", "/api/v1/users?page=1&page_size=10", nil)

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

func TestUserHandler_List_WithFilter(t *testing.T) {
	db := setupUserTestDB(t)
	gin.SetMode(gin.TestMode)

	users := []models.User{
		{Username: "admin", Password: "pass1", Email: "admin@test.com", Status: 1},
		{Username: "user1", Password: "pass2", Email: "user1@test.com", Status: 1},
	}
	for _, u := range users {
		db.Create(&u)
	}

	handler := NewUserHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("GET", "/api/v1/users?username=admin&status=1", nil)

	handler.List(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestUserHandler_Get_Success(t *testing.T) {
	db := setupUserTestDB(t)
	gin.SetMode(gin.TestMode)

	user := models.User{Username: "testuser", Password: "pass", Email: "test@test.com", Status: 1}
	db.Create(&user)

	handler := NewUserHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("GET", "/api/v1/users/1", nil)
	c.Params = gin.Params{{Key: "id", Value: "1"}}

	handler.Get(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestUserHandler_Get_NotFound(t *testing.T) {
	setupUserTestDB(t)
	gin.SetMode(gin.TestMode)

	handler := NewUserHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("GET", "/api/v1/users/999", nil)
	c.Params = gin.Params{{Key: "id", Value: "999"}}

	handler.Get(c)

	if w.Code != http.StatusNotFound {
		t.Errorf("Expected status %d, got %d", http.StatusNotFound, w.Code)
	}
}

func TestUserHandler_Get_InvalidID(t *testing.T) {
	setupUserTestDB(t)
	gin.SetMode(gin.TestMode)

	handler := NewUserHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("GET", "/api/v1/users/invalid", nil)
	c.Params = gin.Params{{Key: "id", Value: "invalid"}}

	handler.Get(c)

	if w.Code != http.StatusBadRequest {
		t.Errorf("Expected status %d, got %d", http.StatusBadRequest, w.Code)
	}
}

func TestUserHandler_Create_Success(t *testing.T) {
	setupUserTestDB(t)
	gin.SetMode(gin.TestMode)

	handler := NewUserHandler()

	req := models.CreateUserRequest{
		Username: "newuser",
		Password: "password123",
		Email:    "new@test.com",
		Nickname: "New User",
	}
	body, _ := json.Marshal(req)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("POST", "/api/v1/users", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")

	handler.Create(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d, body: %s", http.StatusOK, w.Code, w.Body.String())
	}
}

func TestUserHandler_Create_DuplicateUsername(t *testing.T) {
	db := setupUserTestDB(t)
	gin.SetMode(gin.TestMode)

	// 先创建一个用户
	existingUser := models.User{Username: "existinguser", Password: "pass", Email: "exist@test.com"}
	db.Create(&existingUser)

	handler := NewUserHandler()

	req := models.CreateUserRequest{
		Username: "existinguser", // 重复的用户名
		Password: "password123",
		Email:    "new@test.com",
	}
	body, _ := json.Marshal(req)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("POST", "/api/v1/users", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")

	handler.Create(c)

	if w.Code != http.StatusBadRequest {
		t.Errorf("Expected status %d, got %d", http.StatusBadRequest, w.Code)
	}
}

func TestUserHandler_Create_DuplicateEmail(t *testing.T) {
	db := setupUserTestDB(t)
	gin.SetMode(gin.TestMode)

	existingUser := models.User{Username: "existinguser", Password: "pass", Email: "exist@test.com"}
	db.Create(&existingUser)

	handler := NewUserHandler()

	req := models.CreateUserRequest{
		Username: "newuser",
		Password: "password123",
		Email:    "exist@test.com", // 重复的邮箱
	}
	body, _ := json.Marshal(req)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("POST", "/api/v1/users", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")

	handler.Create(c)

	if w.Code != http.StatusBadRequest {
		t.Errorf("Expected status %d, got %d", http.StatusBadRequest, w.Code)
	}
}

func TestUserHandler_Update_Success(t *testing.T) {
	db := setupUserTestDB(t)
	gin.SetMode(gin.TestMode)

	user := models.User{Username: "testuser", Password: "pass", Email: "test@test.com", Status: 1}
	db.Create(&user)

	handler := NewUserHandler()

	status := 0
	req := models.UpdateUserRequest{
		Nickname: "Updated Name",
		Status:   &status,
	}
	body, _ := json.Marshal(req)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("PUT", "/api/v1/users/1", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")
	c.Params = gin.Params{{Key: "id", Value: "1"}}

	handler.Update(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestUserHandler_Delete_Success(t *testing.T) {
	db := setupUserTestDB(t)
	gin.SetMode(gin.TestMode)

	user := models.User{Username: "testuser", Password: "pass", Email: "test@test.com"}
	db.Create(&user)

	handler := NewUserHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("DELETE", "/api/v1/users/1", nil)
	c.Params = gin.Params{{Key: "id", Value: "1"}}

	handler.Delete(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestUserHandler_Delete_AdminProtection(t *testing.T) {
	db := setupUserTestDB(t)
	gin.SetMode(gin.TestMode)

	// 创建admin用户
	admin := models.User{Username: "admin", Password: "pass", Email: "admin@test.com"}
	db.Create(&admin)

	handler := NewUserHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("DELETE", "/api/v1/users/1", nil)
	c.Params = gin.Params{{Key: "id", Value: "1"}}

	handler.Delete(c)

	if w.Code != http.StatusForbidden {
		t.Errorf("Expected status %d, got %d", http.StatusForbidden, w.Code)
	}
}

func TestUserHandler_AssignRoles_Success(t *testing.T) {
	db := setupUserTestDB(t)
	gin.SetMode(gin.TestMode)

	// 创建用户和角色
	user := models.User{Username: "testuser", Password: "pass", Email: "test@test.com"}
	db.Create(&user)

	role := models.Role{Name: "TestRole", Code: "test_role"}
	db.Create(&role)

	handler := NewUserHandler()

	req := models.AssignRolesRequest{
		RoleIDs: []uint{role.ID},
	}
	body, _ := json.Marshal(req)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("PUT", "/api/v1/users/1/roles", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")
	c.Params = gin.Params{{Key: "id", Value: "1"}}

	handler.AssignRoles(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d, body: %s", http.StatusOK, w.Code, w.Body.String())
	}
}

func TestUserHandler_GetUserRoles(t *testing.T) {
	db := setupUserTestDB(t)
	gin.SetMode(gin.TestMode)

	role := models.Role{Name: "TestRole", Code: "test_role"}
	db.Create(&role)

	user := models.User{Username: "testuser", Password: "pass", Email: "test@test.com", Roles: []models.Role{role}}
	db.Create(&user)

	handler := NewUserHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("GET", "/api/v1/users/1/roles", nil)
	c.Params = gin.Params{{Key: "id", Value: "1"}}

	handler.GetUserRoles(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestUserHandler_GetUserPermissions(t *testing.T) {
	db := setupUserTestDB(t)
	gin.SetMode(gin.TestMode)

	perm := models.Permission{Name: "Test Perm", Code: "test:perm", Type: "api"}
	db.Create(&perm)

	role := models.Role{Name: "TestRole", Code: "test_role", Permissions: []models.Permission{perm}}
	db.Create(&role)

	user := models.User{Username: "testuser", Password: "pass", Email: "test@test.com", Roles: []models.Role{role}}
	db.Create(&user)

	handler := NewUserHandler()

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("GET", "/api/v1/users/1/permissions", nil)
	c.Params = gin.Params{{Key: "id", Value: "1"}}

	handler.GetUserPermissions(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestUserHandler_ResetPassword_Success(t *testing.T) {
	db := setupUserTestDB(t)
	gin.SetMode(gin.TestMode)

	user := models.User{Username: "testuser", Password: "oldpass", Email: "test@test.com"}
	db.Create(&user)

	handler := NewUserHandler()

	reqBody := map[string]string{
		"new_password": "newpassword123",
	}
	body, _ := json.Marshal(reqBody)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("PUT", "/api/v1/users/1/password", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")
	c.Params = gin.Params{{Key: "id", Value: "1"}}

	handler.ResetPassword(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestNewUserHandler(t *testing.T) {
	handler := NewUserHandler()
	if handler == nil {
		t.Error("NewUserHandler() should not return nil")
	}
}

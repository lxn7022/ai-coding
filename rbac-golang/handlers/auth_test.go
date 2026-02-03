package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"rbac-golang/config"
	"rbac-golang/database"
	"rbac-golang/models"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

func setupTestDB(t *testing.T) *gorm.DB {
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

func testConfig() *config.Config {
	return &config.Config{
		JWT: config.JWTConfig{
			Secret:     "test-secret-key",
			ExpireTime: 24 * time.Hour,
		},
	}
}

func TestAuthHandler_Login_Success(t *testing.T) {
	db := setupTestDB(t)
	gin.SetMode(gin.TestMode)

	// 创建测试用户
	user := models.User{
		Username: "testuser",
		Password: "password123",
		Email:    "test@test.com",
		Status:   1,
	}
	db.Create(&user)

	// 创建处理器
	cfg := testConfig()
	handler := NewAuthHandler(cfg)

	// 创建请求
	loginReq := models.LoginRequest{
		Username: "testuser",
		Password: "password123",
	}
	body, _ := json.Marshal(loginReq)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("POST", "/api/v1/login", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")

	handler.Login(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}

	var resp Response
	json.Unmarshal(w.Body.Bytes(), &resp)

	if resp.Code != 0 {
		t.Errorf("Expected code 0, got %d", resp.Code)
	}
}

func TestAuthHandler_Login_WrongPassword(t *testing.T) {
	db := setupTestDB(t)
	gin.SetMode(gin.TestMode)

	// 创建测试用户
	user := models.User{
		Username: "testuser",
		Password: "password123",
		Email:    "test@test.com",
		Status:   1,
	}
	db.Create(&user)

	cfg := testConfig()
	handler := NewAuthHandler(cfg)

	loginReq := models.LoginRequest{
		Username: "testuser",
		Password: "wrongpassword",
	}
	body, _ := json.Marshal(loginReq)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("POST", "/api/v1/login", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")

	handler.Login(c)

	if w.Code != http.StatusUnauthorized {
		t.Errorf("Expected status %d, got %d", http.StatusUnauthorized, w.Code)
	}
}

func TestAuthHandler_Login_UserNotFound(t *testing.T) {
	setupTestDB(t)
	gin.SetMode(gin.TestMode)

	cfg := testConfig()
	handler := NewAuthHandler(cfg)

	loginReq := models.LoginRequest{
		Username: "nonexistent",
		Password: "password123",
	}
	body, _ := json.Marshal(loginReq)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("POST", "/api/v1/login", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")

	handler.Login(c)

	if w.Code != http.StatusUnauthorized {
		t.Errorf("Expected status %d, got %d", http.StatusUnauthorized, w.Code)
	}
}

func TestAuthHandler_Login_DisabledUser(t *testing.T) {
	db := setupTestDB(t)
	gin.SetMode(gin.TestMode)

	// 创建禁用的用户（先创建再更新状态，因为GORM会对0值应用默认值）
	user := models.User{
		Username: "disableduser",
		Password: "password123",
		Email:    "disabled@test.com",
	}
	db.Create(&user)
	// 更新为禁用状态
	db.Model(&user).Update("status", 0)

	cfg := testConfig()
	handler := NewAuthHandler(cfg)

	loginReq := models.LoginRequest{
		Username: "disableduser",
		Password: "password123",
	}
	body, _ := json.Marshal(loginReq)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("POST", "/api/v1/login", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")

	handler.Login(c)

	if w.Code != http.StatusForbidden {
		t.Errorf("Expected status %d, got %d", http.StatusForbidden, w.Code)
	}
}

func TestAuthHandler_Login_InvalidRequest(t *testing.T) {
	setupTestDB(t)
	gin.SetMode(gin.TestMode)

	cfg := testConfig()
	handler := NewAuthHandler(cfg)

	// 无效的JSON
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("POST", "/api/v1/login", bytes.NewBuffer([]byte("invalid json")))
	c.Request.Header.Set("Content-Type", "application/json")

	handler.Login(c)

	if w.Code != http.StatusBadRequest {
		t.Errorf("Expected status %d, got %d", http.StatusBadRequest, w.Code)
	}
}

func TestAuthHandler_GetCurrentUser_Success(t *testing.T) {
	db := setupTestDB(t)
	gin.SetMode(gin.TestMode)

	// 创建测试用户
	user := models.User{
		Username: "testuser",
		Password: "password123",
		Email:    "test@test.com",
		Status:   1,
	}
	db.Create(&user)

	cfg := testConfig()
	handler := NewAuthHandler(cfg)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Set("userID", user.ID)

	handler.GetCurrentUser(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestAuthHandler_GetCurrentUser_NoLogin(t *testing.T) {
	setupTestDB(t)
	gin.SetMode(gin.TestMode)

	cfg := testConfig()
	handler := NewAuthHandler(cfg)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	// 不设置userID

	handler.GetCurrentUser(c)

	if w.Code != http.StatusUnauthorized {
		t.Errorf("Expected status %d, got %d", http.StatusUnauthorized, w.Code)
	}
}

func TestAuthHandler_GetCurrentUser_UserNotFound(t *testing.T) {
	setupTestDB(t)
	gin.SetMode(gin.TestMode)

	cfg := testConfig()
	handler := NewAuthHandler(cfg)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Set("userID", uint(9999)) // 不存在的用户ID

	handler.GetCurrentUser(c)

	if w.Code != http.StatusNotFound {
		t.Errorf("Expected status %d, got %d", http.StatusNotFound, w.Code)
	}
}

func TestAuthHandler_ChangePassword_Success(t *testing.T) {
	db := setupTestDB(t)
	gin.SetMode(gin.TestMode)

	// 创建测试用户
	user := models.User{
		Username: "testuser",
		Password: "oldpassword",
		Email:    "test@test.com",
		Status:   1,
	}
	db.Create(&user)

	cfg := testConfig()
	handler := NewAuthHandler(cfg)

	reqBody := map[string]string{
		"old_password": "oldpassword",
		"new_password": "newpassword123",
	}
	body, _ := json.Marshal(reqBody)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("PUT", "/api/v1/me/password", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")
	c.Set("userID", user.ID)

	handler.ChangePassword(c)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d, body: %s", http.StatusOK, w.Code, w.Body.String())
	}
}

func TestAuthHandler_ChangePassword_WrongOldPassword(t *testing.T) {
	db := setupTestDB(t)
	gin.SetMode(gin.TestMode)

	user := models.User{
		Username: "testuser",
		Password: "oldpassword",
		Email:    "test@test.com",
		Status:   1,
	}
	db.Create(&user)

	cfg := testConfig()
	handler := NewAuthHandler(cfg)

	reqBody := map[string]string{
		"old_password": "wrongoldpassword",
		"new_password": "newpassword123",
	}
	body, _ := json.Marshal(reqBody)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest("PUT", "/api/v1/me/password", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")
	c.Set("userID", user.ID)

	handler.ChangePassword(c)

	if w.Code != http.StatusBadRequest {
		t.Errorf("Expected status %d, got %d", http.StatusBadRequest, w.Code)
	}
}

func TestClaims_Structure(t *testing.T) {
	claims := Claims{
		UserID:   1,
		Username: "testuser",
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(24 * time.Hour)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			Issuer:    "rbac-system",
		},
	}

	if claims.UserID != 1 {
		t.Errorf("UserID = %d, want 1", claims.UserID)
	}
	if claims.Username != "testuser" {
		t.Errorf("Username = %s, want testuser", claims.Username)
	}
	if claims.Issuer != "rbac-system" {
		t.Errorf("Issuer = %s, want rbac-system", claims.Issuer)
	}
}

func TestAuthHandler_GenerateToken(t *testing.T) {
	cfg := testConfig()
	handler := NewAuthHandler(cfg)

	user := &models.User{
		Username: "testuser",
	}
	user.ID = 1

	token, err := handler.generateToken(user)
	if err != nil {
		t.Fatalf("generateToken() error = %v", err)
	}

	if token == "" {
		t.Error("Token should not be empty")
	}

	// 验证token可以被解析
	claims := &Claims{}
	parsedToken, err := jwt.ParseWithClaims(token, claims, func(token *jwt.Token) (interface{}, error) {
		return []byte(cfg.JWT.Secret), nil
	})

	if err != nil {
		t.Fatalf("Failed to parse token: %v", err)
	}

	if !parsedToken.Valid {
		t.Error("Token should be valid")
	}

	if claims.UserID != 1 {
		t.Errorf("Claims.UserID = %d, want 1", claims.UserID)
	}
	if claims.Username != "testuser" {
		t.Errorf("Claims.Username = %s, want testuser", claims.Username)
	}
}

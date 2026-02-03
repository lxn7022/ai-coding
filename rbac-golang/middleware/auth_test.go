package middleware

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"rbac-golang/config"
	"rbac-golang/database"
	"rbac-golang/handlers"
	"rbac-golang/models"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

func setupMiddlewareTestDB(t *testing.T) *gorm.DB {
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

func testMiddlewareConfig() *config.Config {
	return &config.Config{
		JWT: config.JWTConfig{
			Secret:     "test-middleware-secret",
			ExpireTime: 24 * time.Hour,
		},
	}
}

func generateTestToken(userID uint, username, secret string, expired bool) string {
	expTime := time.Now().Add(24 * time.Hour)
	if expired {
		expTime = time.Now().Add(-24 * time.Hour) // 过期的token
	}

	claims := handlers.Claims{
		UserID:   userID,
		Username: username,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(expTime),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			Issuer:    "rbac-system",
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, _ := token.SignedString([]byte(secret))
	return tokenString
}

func TestAuthMiddleware_Success(t *testing.T) {
	db := setupMiddlewareTestDB(t)
	gin.SetMode(gin.TestMode)

	// 创建测试用户
	user := models.User{Username: "testuser", Password: "pass", Status: 1}
	db.Create(&user)

	cfg := testMiddlewareConfig()
	token := generateTestToken(user.ID, user.Username, cfg.JWT.Secret, false)

	router := gin.New()
	router.Use(AuthMiddleware(cfg))
	router.GET("/test", func(c *gin.Context) {
		userID, _ := c.Get("userID")
		username, _ := c.Get("username")
		c.JSON(200, gin.H{"userID": userID, "username": username})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/test", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	router.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestAuthMiddleware_NoAuthHeader(t *testing.T) {
	setupMiddlewareTestDB(t)
	gin.SetMode(gin.TestMode)

	cfg := testMiddlewareConfig()

	router := gin.New()
	router.Use(AuthMiddleware(cfg))
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/test", nil)
	// 不设置Authorization头

	router.ServeHTTP(w, req)

	if w.Code != http.StatusUnauthorized {
		t.Errorf("Expected status %d, got %d", http.StatusUnauthorized, w.Code)
	}
}

func TestAuthMiddleware_InvalidFormat(t *testing.T) {
	setupMiddlewareTestDB(t)
	gin.SetMode(gin.TestMode)

	cfg := testMiddlewareConfig()

	router := gin.New()
	router.Use(AuthMiddleware(cfg))
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	tests := []struct {
		name   string
		header string
	}{
		{"只有Bearer", "Bearer"},
		{"没有Bearer前缀", "token123"},
		{"错误的前缀", "Basic token123"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("GET", "/test", nil)
			req.Header.Set("Authorization", tt.header)

			router.ServeHTTP(w, req)

			if w.Code != http.StatusUnauthorized {
				t.Errorf("Expected status %d, got %d", http.StatusUnauthorized, w.Code)
			}
		})
	}
}

func TestAuthMiddleware_InvalidToken(t *testing.T) {
	setupMiddlewareTestDB(t)
	gin.SetMode(gin.TestMode)

	cfg := testMiddlewareConfig()

	router := gin.New()
	router.Use(AuthMiddleware(cfg))
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/test", nil)
	req.Header.Set("Authorization", "Bearer invalid-token")

	router.ServeHTTP(w, req)

	if w.Code != http.StatusUnauthorized {
		t.Errorf("Expected status %d, got %d", http.StatusUnauthorized, w.Code)
	}
}

func TestAuthMiddleware_ExpiredToken(t *testing.T) {
	setupMiddlewareTestDB(t)
	gin.SetMode(gin.TestMode)

	cfg := testMiddlewareConfig()
	token := generateTestToken(1, "testuser", cfg.JWT.Secret, true) // 过期的token

	router := gin.New()
	router.Use(AuthMiddleware(cfg))
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/test", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	router.ServeHTTP(w, req)

	if w.Code != http.StatusUnauthorized {
		t.Errorf("Expected status %d, got %d", http.StatusUnauthorized, w.Code)
	}
}

func TestAuthMiddleware_UserNotFound(t *testing.T) {
	setupMiddlewareTestDB(t)
	gin.SetMode(gin.TestMode)

	cfg := testMiddlewareConfig()
	token := generateTestToken(999, "nonexistent", cfg.JWT.Secret, false) // 不存在的用户

	router := gin.New()
	router.Use(AuthMiddleware(cfg))
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/test", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	router.ServeHTTP(w, req)

	if w.Code != http.StatusUnauthorized {
		t.Errorf("Expected status %d, got %d", http.StatusUnauthorized, w.Code)
	}
}

func TestAuthMiddleware_DisabledUser(t *testing.T) {
	db := setupMiddlewareTestDB(t)
	gin.SetMode(gin.TestMode)

	// 创建禁用的用户（先创建再更新状态，因为GORM会对0值应用默认值）
	user := models.User{Username: "disabled", Password: "pass"}
	db.Create(&user)
	db.Model(&user).Update("status", 0)

	cfg := testMiddlewareConfig()
	token := generateTestToken(user.ID, user.Username, cfg.JWT.Secret, false)

	router := gin.New()
	router.Use(AuthMiddleware(cfg))
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/test", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	router.ServeHTTP(w, req)

	if w.Code != http.StatusForbidden {
		t.Errorf("Expected status %d, got %d", http.StatusForbidden, w.Code)
	}
}

func TestPermissionMiddleware_Success(t *testing.T) {
	db := setupMiddlewareTestDB(t)
	gin.SetMode(gin.TestMode)

	// 创建权限
	perm := models.Permission{Name: "Test Perm", Code: "test:read", Type: "api"}
	db.Create(&perm)

	// 创建角色并关联权限
	role := models.Role{Name: "TestRole", Code: "test_role", Permissions: []models.Permission{perm}}
	db.Create(&role)

	// 创建用户并关联角色
	user := models.User{Username: "testuser", Password: "pass", Status: 1, Roles: []models.Role{role}}
	db.Create(&user)

	router := gin.New()
	router.Use(func(c *gin.Context) {
		c.Set("userID", user.ID)
		c.Next()
	})
	router.Use(PermissionMiddleware("test:read"))
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/test", nil)

	router.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestPermissionMiddleware_NoLogin(t *testing.T) {
	setupMiddlewareTestDB(t)
	gin.SetMode(gin.TestMode)

	router := gin.New()
	// 不设置userID
	router.Use(PermissionMiddleware("test:read"))
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/test", nil)

	router.ServeHTTP(w, req)

	if w.Code != http.StatusUnauthorized {
		t.Errorf("Expected status %d, got %d", http.StatusUnauthorized, w.Code)
	}
}

func TestPermissionMiddleware_NoPermission(t *testing.T) {
	db := setupMiddlewareTestDB(t)
	gin.SetMode(gin.TestMode)

	// 创建用户，没有任何权限
	user := models.User{Username: "testuser", Password: "pass", Status: 1}
	db.Create(&user)

	router := gin.New()
	router.Use(func(c *gin.Context) {
		c.Set("userID", user.ID)
		c.Next()
	})
	router.Use(PermissionMiddleware("test:read"))
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/test", nil)

	router.ServeHTTP(w, req)

	if w.Code != http.StatusForbidden {
		t.Errorf("Expected status %d, got %d", http.StatusForbidden, w.Code)
	}
}

func TestPermissionMiddleware_AdminBypass(t *testing.T) {
	db := setupMiddlewareTestDB(t)
	gin.SetMode(gin.TestMode)

	// 创建admin角色（没有具体权限，但admin角色会绕过权限检查）
	adminRole := models.Role{Name: "Admin", Code: "admin"}
	db.Create(&adminRole)

	// 创建用户并关联admin角色
	user := models.User{Username: "admin", Password: "pass", Status: 1, Roles: []models.Role{adminRole}}
	db.Create(&user)

	router := gin.New()
	router.Use(func(c *gin.Context) {
		c.Set("userID", user.ID)
		c.Next()
	})
	router.Use(PermissionMiddleware("any:permission")) // 任意权限都应该通过
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/test", nil)

	router.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d (admin should bypass permission check)", http.StatusOK, w.Code)
	}
}

func TestRoleMiddleware_Success(t *testing.T) {
	db := setupMiddlewareTestDB(t)
	gin.SetMode(gin.TestMode)

	role := models.Role{Name: "Editor", Code: "editor"}
	db.Create(&role)

	user := models.User{Username: "testuser", Password: "pass", Status: 1, Roles: []models.Role{role}}
	db.Create(&user)

	router := gin.New()
	router.Use(func(c *gin.Context) {
		c.Set("userID", user.ID)
		c.Next()
	})
	router.Use(RoleMiddleware("editor", "admin"))
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/test", nil)

	router.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestRoleMiddleware_NoLogin(t *testing.T) {
	setupMiddlewareTestDB(t)
	gin.SetMode(gin.TestMode)

	router := gin.New()
	router.Use(RoleMiddleware("admin"))
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/test", nil)

	router.ServeHTTP(w, req)

	if w.Code != http.StatusUnauthorized {
		t.Errorf("Expected status %d, got %d", http.StatusUnauthorized, w.Code)
	}
}

func TestRoleMiddleware_NoRole(t *testing.T) {
	db := setupMiddlewareTestDB(t)
	gin.SetMode(gin.TestMode)

	user := models.User{Username: "testuser", Password: "pass", Status: 1}
	db.Create(&user)

	router := gin.New()
	router.Use(func(c *gin.Context) {
		c.Set("userID", user.ID)
		c.Next()
	})
	router.Use(RoleMiddleware("admin"))
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/test", nil)

	router.ServeHTTP(w, req)

	if w.Code != http.StatusForbidden {
		t.Errorf("Expected status %d, got %d", http.StatusForbidden, w.Code)
	}
}

func TestAdminMiddleware_Success(t *testing.T) {
	db := setupMiddlewareTestDB(t)
	gin.SetMode(gin.TestMode)

	adminRole := models.Role{Name: "Admin", Code: "admin"}
	db.Create(&adminRole)

	user := models.User{Username: "admin", Password: "pass", Status: 1, Roles: []models.Role{adminRole}}
	db.Create(&user)

	router := gin.New()
	router.Use(func(c *gin.Context) {
		c.Set("userID", user.ID)
		c.Next()
	})
	router.Use(AdminMiddleware())
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/test", nil)

	router.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestAdminMiddleware_NotAdmin(t *testing.T) {
	db := setupMiddlewareTestDB(t)
	gin.SetMode(gin.TestMode)

	userRole := models.Role{Name: "User", Code: "user"}
	db.Create(&userRole)

	user := models.User{Username: "testuser", Password: "pass", Status: 1, Roles: []models.Role{userRole}}
	db.Create(&user)

	router := gin.New()
	router.Use(func(c *gin.Context) {
		c.Set("userID", user.ID)
		c.Next()
	})
	router.Use(AdminMiddleware())
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/test", nil)

	router.ServeHTTP(w, req)

	if w.Code != http.StatusForbidden {
		t.Errorf("Expected status %d, got %d", http.StatusForbidden, w.Code)
	}
}

func TestPermissionMiddleware_UserNotFound(t *testing.T) {
	setupMiddlewareTestDB(t)
	gin.SetMode(gin.TestMode)

	router := gin.New()
	router.Use(func(c *gin.Context) {
		c.Set("userID", uint(999)) // 不存在的用户
		c.Next()
	})
	router.Use(PermissionMiddleware("test:read"))
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/test", nil)

	router.ServeHTTP(w, req)

	if w.Code != http.StatusUnauthorized {
		t.Errorf("Expected status %d, got %d", http.StatusUnauthorized, w.Code)
	}
}

func TestRoleMiddleware_UserNotFound(t *testing.T) {
	setupMiddlewareTestDB(t)
	gin.SetMode(gin.TestMode)

	router := gin.New()
	router.Use(func(c *gin.Context) {
		c.Set("userID", uint(999)) // 不存在的用户
		c.Next()
	})
	router.Use(RoleMiddleware("admin"))
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/test", nil)

	router.ServeHTTP(w, req)

	if w.Code != http.StatusUnauthorized {
		t.Errorf("Expected status %d, got %d", http.StatusUnauthorized, w.Code)
	}
}

package models

import (
	"testing"

	"golang.org/x/crypto/bcrypt"
)

func TestUser_HashPassword(t *testing.T) {
	user := &User{
		Username: "testuser",
		Password: "password123",
	}

	err := user.hashPassword()
	if err != nil {
		t.Fatalf("hashPassword() error = %v", err)
	}

	// 验证密码已被哈希
	if user.Password == "password123" {
		t.Error("Password should be hashed")
	}

	// 验证哈希后的密码可以被验证
	err = bcrypt.CompareHashAndPassword([]byte(user.Password), []byte("password123"))
	if err != nil {
		t.Error("Hashed password should match original")
	}
}

func TestUser_CheckPassword(t *testing.T) {
	tests := []struct {
		name           string
		storedPassword string
		inputPassword  string
		want           bool
	}{
		{
			name:           "正确密码",
			storedPassword: "correct123",
			inputPassword:  "correct123",
			want:           true,
		},
		{
			name:           "错误密码",
			storedPassword: "correct123",
			inputPassword:  "wrong456",
			want:           false,
		},
		{
			name:           "空密码输入",
			storedPassword: "correct123",
			inputPassword:  "",
			want:           false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// 先对存储密码进行哈希
			hashedPassword, _ := bcrypt.GenerateFromPassword([]byte(tt.storedPassword), bcrypt.DefaultCost)
			user := &User{
				Password: string(hashedPassword),
			}

			if got := user.CheckPassword(tt.inputPassword); got != tt.want {
				t.Errorf("CheckPassword() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestUser_SetPassword(t *testing.T) {
	user := &User{}

	err := user.SetPassword("newpassword")
	if err != nil {
		t.Fatalf("SetPassword() error = %v", err)
	}

	// 验证新密码可以被验证
	if !user.CheckPassword("newpassword") {
		t.Error("New password should be verifiable")
	}

	// 验证旧密码不能通过
	if user.CheckPassword("oldpassword") {
		t.Error("Old password should not work")
	}
}

func TestUser_HasPermission(t *testing.T) {
	user := &User{
		Roles: []Role{
			{
				Code: "admin",
				Permissions: []Permission{
					{Code: "user:list"},
					{Code: "user:create"},
				},
			},
			{
				Code: "editor",
				Permissions: []Permission{
					{Code: "article:edit"},
				},
			},
		},
	}

	tests := []struct {
		name           string
		permissionCode string
		want           bool
	}{
		{"拥有的权限1", "user:list", true},
		{"拥有的权限2", "user:create", true},
		{"另一个角色的权限", "article:edit", true},
		{"不存在的权限", "user:delete", false},
		{"空权限码", "", false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := user.HasPermission(tt.permissionCode); got != tt.want {
				t.Errorf("HasPermission(%q) = %v, want %v", tt.permissionCode, got, tt.want)
			}
		})
	}
}

func TestUser_HasPermission_EmptyRoles(t *testing.T) {
	user := &User{
		Roles: []Role{},
	}

	if user.HasPermission("any:permission") {
		t.Error("User with no roles should not have any permission")
	}
}

func TestUser_HasRole(t *testing.T) {
	user := &User{
		Roles: []Role{
			{Code: "admin"},
			{Code: "editor"},
		},
	}

	tests := []struct {
		name     string
		roleCode string
		want     bool
	}{
		{"拥有admin角色", "admin", true},
		{"拥有editor角色", "editor", true},
		{"不存在的角色", "viewer", false},
		{"空角色码", "", false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := user.HasRole(tt.roleCode); got != tt.want {
				t.Errorf("HasRole(%q) = %v, want %v", tt.roleCode, got, tt.want)
			}
		})
	}
}

func TestUser_HasRole_EmptyRoles(t *testing.T) {
	user := &User{
		Roles: []Role{},
	}

	if user.HasRole("any") {
		t.Error("User with no roles should not have any role")
	}
}

func TestUser_TableName(t *testing.T) {
	user := User{}
	if tableName := user.TableName(); tableName != "users" {
		t.Errorf("TableName() = %v, want %v", tableName, "users")
	}
}

func TestCreateUserRequest_Validation(t *testing.T) {
	// 测试请求结构体的字段
	req := CreateUserRequest{
		Username: "testuser",
		Password: "123456",
		Email:    "test@example.com",
		Nickname: "Test",
	}

	if req.Username == "" {
		t.Error("Username should not be empty")
	}
	if len(req.Password) < 6 {
		t.Error("Password should be at least 6 characters")
	}
}

func TestLoginRequest_Fields(t *testing.T) {
	req := LoginRequest{
		Username: "admin",
		Password: "password",
	}

	if req.Username == "" || req.Password == "" {
		t.Error("LoginRequest fields should not be empty")
	}
}

func TestAssignRolesRequest_Fields(t *testing.T) {
	req := AssignRolesRequest{
		RoleIDs: []uint{1, 2, 3},
	}

	if len(req.RoleIDs) != 3 {
		t.Errorf("RoleIDs length = %d, want 3", len(req.RoleIDs))
	}
}

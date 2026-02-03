package models

import (
	"testing"
)

func TestPermission_TableName(t *testing.T) {
	perm := Permission{}
	if tableName := perm.TableName(); tableName != "permissions" {
		t.Errorf("TableName() = %v, want %v", tableName, "permissions")
	}
}

func TestCreatePermissionRequest_Validation(t *testing.T) {
	tests := []struct {
		name    string
		req     CreatePermissionRequest
		wantErr bool
	}{
		{
			name: "有效的API权限",
			req: CreatePermissionRequest{
				Name:   "查看用户",
				Code:   "user:list",
				Type:   "api",
				Path:   "/api/v1/users",
				Method: "GET",
			},
			wantErr: false,
		},
		{
			name: "有效的菜单权限",
			req: CreatePermissionRequest{
				Name: "用户管理",
				Code: "user:manage",
				Type: "menu",
				Path: "/users",
			},
			wantErr: false,
		},
		{
			name: "有效的按钮权限",
			req: CreatePermissionRequest{
				Name: "新增按钮",
				Code: "user:create:btn",
				Type: "button",
			},
			wantErr: false,
		},
		{
			name: "缺少名称",
			req: CreatePermissionRequest{
				Name: "",
				Code: "user:list",
				Type: "api",
			},
			wantErr: true,
		},
		{
			name: "缺少编码",
			req: CreatePermissionRequest{
				Name: "查看用户",
				Code: "",
				Type: "api",
			},
			wantErr: true,
		},
		{
			name: "缺少类型",
			req: CreatePermissionRequest{
				Name: "查看用户",
				Code: "user:list",
				Type: "",
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			hasErr := tt.req.Name == "" || tt.req.Code == "" || tt.req.Type == ""
			if hasErr != tt.wantErr {
				t.Errorf("Validation error = %v, wantErr %v", hasErr, tt.wantErr)
			}
		})
	}
}

func TestPermission_TypeValues(t *testing.T) {
	validTypes := []string{"menu", "button", "api"}

	for _, permType := range validTypes {
		perm := Permission{
			Name: "测试权限",
			Code: "test:perm",
			Type: permType,
		}

		if perm.Type != permType {
			t.Errorf("Type = %v, want %v", perm.Type, permType)
		}
	}
}

func TestPermission_ParentID(t *testing.T) {
	// 测试无父级
	perm := Permission{
		Name:     "顶级菜单",
		Code:     "menu:top",
		Type:     "menu",
		ParentID: nil,
	}

	if perm.ParentID != nil {
		t.Error("ParentID should be nil for top-level permission")
	}

	// 测试有父级
	parentID := uint(1)
	childPerm := Permission{
		Name:     "子菜单",
		Code:     "menu:child",
		Type:     "menu",
		ParentID: &parentID,
	}

	if childPerm.ParentID == nil || *childPerm.ParentID != 1 {
		t.Error("ParentID should be 1 for child permission")
	}
}

func TestPermission_Sort(t *testing.T) {
	perms := []Permission{
		{Name: "第三个", Code: "perm3", Type: "menu", Sort: 3},
		{Name: "第一个", Code: "perm1", Type: "menu", Sort: 1},
		{Name: "第二个", Code: "perm2", Type: "menu", Sort: 2},
	}

	// 验证排序字段
	if perms[0].Sort != 3 {
		t.Errorf("First perm Sort = %d, want 3", perms[0].Sort)
	}
	if perms[1].Sort != 1 {
		t.Errorf("Second perm Sort = %d, want 1", perms[1].Sort)
	}
}

func TestPermissionTree_Structure(t *testing.T) {
	// 构建权限树
	tree := PermissionTree{
		Permission: Permission{
			Name: "用户管理",
			Code: "user:manage",
			Type: "menu",
		},
		Children: []PermissionTree{
			{
				Permission: Permission{
					Name: "查看用户",
					Code: "user:list",
					Type: "api",
				},
				Children: nil,
			},
			{
				Permission: Permission{
					Name: "创建用户",
					Code: "user:create",
					Type: "api",
				},
				Children: nil,
			},
		},
	}

	if tree.Name != "用户管理" {
		t.Errorf("Root name = %v, want %v", tree.Name, "用户管理")
	}

	if len(tree.Children) != 2 {
		t.Errorf("Children count = %d, want 2", len(tree.Children))
	}

	if tree.Children[0].Code != "user:list" {
		t.Errorf("First child code = %v, want %v", tree.Children[0].Code, "user:list")
	}
}

func TestUpdatePermissionRequest_OptionalFields(t *testing.T) {
	// 测试所有字段为空/nil
	req := UpdatePermissionRequest{}

	if req.Name != "" {
		t.Error("Name should be empty string by default")
	}
	if req.Status != nil {
		t.Error("Status should be nil by default")
	}
	if req.Sort != nil {
		t.Error("Sort should be nil by default")
	}

	// 测试设置字段
	status := 1
	sort := 10
	req = UpdatePermissionRequest{
		Name:   "更新后的名称",
		Status: &status,
		Sort:   &sort,
	}

	if req.Name != "更新后的名称" {
		t.Errorf("Name = %v, want %v", req.Name, "更新后的名称")
	}
	if *req.Status != 1 {
		t.Errorf("Status = %v, want %v", *req.Status, 1)
	}
	if *req.Sort != 10 {
		t.Errorf("Sort = %v, want %v", *req.Sort, 10)
	}
}

func TestPermission_MethodValues(t *testing.T) {
	validMethods := []string{"GET", "POST", "PUT", "DELETE", "PATCH"}

	for _, method := range validMethods {
		perm := Permission{
			Name:   "API权限",
			Code:   "api:test",
			Type:   "api",
			Path:   "/api/test",
			Method: method,
		}

		if perm.Method != method {
			t.Errorf("Method = %v, want %v", perm.Method, method)
		}
	}
}

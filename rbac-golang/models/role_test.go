package models

import (
	"testing"
)

func TestRole_TableName(t *testing.T) {
	role := Role{}
	if tableName := role.TableName(); tableName != "roles" {
		t.Errorf("TableName() = %v, want %v", tableName, "roles")
	}
}

func TestCreateRoleRequest_Fields(t *testing.T) {
	tests := []struct {
		name    string
		req     CreateRoleRequest
		wantErr bool
	}{
		{
			name: "有效请求",
			req: CreateRoleRequest{
				Name:        "管理员",
				Code:        "admin",
				Description: "系统管理员",
			},
			wantErr: false,
		},
		{
			name: "缺少名称",
			req: CreateRoleRequest{
				Name:        "",
				Code:        "admin",
				Description: "系统管理员",
			},
			wantErr: true,
		},
		{
			name: "缺少编码",
			req: CreateRoleRequest{
				Name:        "管理员",
				Code:        "",
				Description: "系统管理员",
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			hasErr := tt.req.Name == "" || tt.req.Code == ""
			if hasErr != tt.wantErr {
				t.Errorf("Validation error = %v, wantErr %v", hasErr, tt.wantErr)
			}
		})
	}
}

func TestUpdateRoleRequest_StatusPointer(t *testing.T) {
	// 测试状态指针为nil时不更新
	req := UpdateRoleRequest{
		Name:   "新名称",
		Status: nil,
	}

	if req.Status != nil {
		t.Error("Status should be nil when not set")
	}

	// 测试状态指针有值时可以更新
	status := 0
	req.Status = &status

	if req.Status == nil || *req.Status != 0 {
		t.Error("Status should be 0 when set")
	}
}

func TestAssignPermissionsRequest_Fields(t *testing.T) {
	req := AssignPermissionsRequest{
		PermissionIDs: []uint{1, 2, 3, 4, 5},
	}

	if len(req.PermissionIDs) != 5 {
		t.Errorf("PermissionIDs length = %d, want 5", len(req.PermissionIDs))
	}

	// 测试空数组
	emptyReq := AssignPermissionsRequest{
		PermissionIDs: []uint{},
	}

	if len(emptyReq.PermissionIDs) != 0 {
		t.Error("Empty PermissionIDs should have length 0")
	}
}

func TestRole_Fields(t *testing.T) {
	role := Role{
		Name:        "测试角色",
		Code:        "test_role",
		Description: "这是一个测试角色",
		Status:      1,
		Permissions: []Permission{
			{Code: "test:read"},
			{Code: "test:write"},
		},
	}

	if role.Name != "测试角色" {
		t.Errorf("Name = %v, want %v", role.Name, "测试角色")
	}

	if role.Code != "test_role" {
		t.Errorf("Code = %v, want %v", role.Code, "test_role")
	}

	if role.Status != 1 {
		t.Errorf("Status = %v, want %v", role.Status, 1)
	}

	if len(role.Permissions) != 2 {
		t.Errorf("Permissions length = %d, want 2", len(role.Permissions))
	}
}

#pragma once

#include <string>
#include <unordered_set>
#include <vector>

namespace rbac {

// 权限：格式通常为 "资源:操作"，如 "user:read", "order:write"
using PermissionId = std::string;

// 角色 ID
using RoleId = std::string;

// 用户 ID
using UserId = std::string;

// 权限定义（可扩展描述）
struct Permission {
    PermissionId id;
    std::string name;
    std::string description;
};

// 角色
struct Role {
    RoleId id;
    std::string name;
    std::string description;
    std::unordered_set<PermissionId> permissions;
};

// 用户
struct User {
    UserId id;
    std::string name;
    std::unordered_set<RoleId> roles;
};

}  // namespace rbac

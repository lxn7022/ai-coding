#pragma once

#include "rbac/types.hpp"
#include <memory>
#include <optional>
#include <unordered_map>

namespace rbac {

/**
 * RBAC 引擎：基于角色的访问控制核心
 * - 用户 -> 角色（多对多）
 * - 角色 -> 权限（多对多）
 * - 检查：用户是否拥有某权限（通过其角色）
 */
class RbacEngine {
public:
    RbacEngine() = default;
    ~RbacEngine() = default;

    // ---------- 用户 ----------
    bool addUser(const UserId& id, const std::string& name);
    bool removeUser(const UserId& id);
    std::optional<User> getUser(const UserId& id) const;
    std::vector<User> listUsers() const;

    // ---------- 角色 ----------
    bool addRole(const RoleId& id, const std::string& name,
                 const std::string& description = "");
    bool removeRole(const RoleId& id);
    std::optional<Role> getRole(const RoleId& id) const;
    std::vector<Role> listRoles() const;

    // ---------- 权限 ----------
    bool addPermission(const PermissionId& id, const std::string& name = "",
                       const std::string& description = "");
    bool removePermission(const PermissionId& id);
    std::optional<Permission> getPermission(const PermissionId& id) const;
    std::vector<Permission> listPermissions() const;

    // ---------- 分配关系 ----------
    bool assignRoleToUser(const UserId& userId, const RoleId& roleId);
    bool revokeRoleFromUser(const UserId& userId, const RoleId& roleId);
    bool assignPermissionToRole(const RoleId& roleId, const PermissionId& permId);
    bool revokePermissionFromRole(const RoleId& roleId, const PermissionId& permId);

    // ---------- 权限检查 ----------
    /// 判断用户是否拥有指定权限（通过其任意角色）
    bool hasPermission(const UserId& userId, const PermissionId& permissionId) const;
    /// 判断用户是否拥有全部指定权限
    bool hasAllPermissions(const UserId& userId,
                          const std::vector<PermissionId>& permissionIds) const;
    /// 判断用户是否拥有任意指定权限
    bool hasAnyPermission(const UserId& userId,
                         const std::vector<PermissionId>& permissionIds) const;

    // ---------- 查询 ----------
    std::vector<RoleId> getRolesForUser(const UserId& userId) const;
    std::vector<PermissionId> getPermissionsForUser(const UserId& userId) const;
    std::vector<PermissionId> getPermissionsForRole(const RoleId& roleId) const;

private:
    std::unordered_map<UserId, User> users_;
    std::unordered_map<RoleId, Role> roles_;
    std::unordered_map<PermissionId, Permission> permissions_;
};

}  // namespace rbac

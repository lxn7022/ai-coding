#include "rbac/rbac_engine.hpp"
#include <algorithm>
#include <unordered_set>

namespace rbac {

// ---------- 用户 ----------
bool RbacEngine::addUser(const UserId& id, const std::string& name) {
    if (users_.count(id)) return false;
    users_[id] = User{id, name, {}};
    return true;
}

bool RbacEngine::removeUser(const UserId& id) {
    auto it = users_.find(id);
    if (it == users_.end()) return false;
    users_.erase(it);
    return true;
}

std::optional<User> RbacEngine::getUser(const UserId& id) const {
    auto it = users_.find(id);
    if (it == users_.end()) return std::nullopt;
    return it->second;
}

std::vector<User> RbacEngine::listUsers() const {
    std::vector<User> result;
    result.reserve(users_.size());
    for (const auto& [_, u] : users_) result.push_back(u);
    return result;
}

// ---------- 角色 ----------
bool RbacEngine::addRole(const RoleId& id, const std::string& name,
                         const std::string& description) {
    if (roles_.count(id)) return false;
    roles_[id] = Role{id, name, description, {}};
    return true;
}

bool RbacEngine::removeRole(const RoleId& id) {
    auto it = roles_.find(id);
    if (it == roles_.end()) return false;
    // 从所有用户中移除该角色引用
    for (auto& [_, u] : users_) u.roles.erase(id);
    roles_.erase(it);
    return true;
}

std::optional<Role> RbacEngine::getRole(const RoleId& id) const {
    auto it = roles_.find(id);
    if (it == roles_.end()) return std::nullopt;
    return it->second;
}

std::vector<Role> RbacEngine::listRoles() const {
    std::vector<Role> result;
    result.reserve(roles_.size());
    for (const auto& [_, r] : roles_) result.push_back(r);
    return result;
}

// ---------- 权限 ----------
bool RbacEngine::addPermission(const PermissionId& id, const std::string& name,
                               const std::string& description) {
    if (permissions_.count(id)) return false;
    permissions_[id] = Permission{id, name.empty() ? id : name, description};
    return true;
}

bool RbacEngine::removePermission(const PermissionId& id) {
    auto it = permissions_.find(id);
    if (it == permissions_.end()) return false;
    for (auto& [_, r] : roles_) r.permissions.erase(id);
    permissions_.erase(it);
    return true;
}

std::optional<Permission> RbacEngine::getPermission(const PermissionId& id) const {
    auto it = permissions_.find(id);
    if (it == permissions_.end()) return std::nullopt;
    return it->second;
}

std::vector<Permission> RbacEngine::listPermissions() const {
    std::vector<Permission> result;
    result.reserve(permissions_.size());
    for (const auto& [_, p] : permissions_) result.push_back(p);
    return result;
}

// ---------- 分配关系 ----------
bool RbacEngine::assignRoleToUser(const UserId& userId, const RoleId& roleId) {
    auto uIt = users_.find(userId);
    auto rIt = roles_.find(roleId);
    if (uIt == users_.end() || rIt == roles_.end()) return false;
    uIt->second.roles.insert(roleId);
    return true;
}

bool RbacEngine::revokeRoleFromUser(const UserId& userId, const RoleId& roleId) {
    auto it = users_.find(userId);
    if (it == users_.end()) return false;
    return it->second.roles.erase(roleId) > 0;
}

bool RbacEngine::assignPermissionToRole(const RoleId& roleId,
                                        const PermissionId& permId) {
    auto rIt = roles_.find(roleId);
    if (rIt == roles_.end()) return false;
    // 权限可以不存在于 permissions_ 中，仅作为字符串使用；若需校验可取消下面注释
    // if (!permissions_.count(permId)) return false;
    rIt->second.permissions.insert(permId);
    return true;
}

bool RbacEngine::revokePermissionFromRole(const RoleId& roleId,
                                          const PermissionId& permId) {
    auto it = roles_.find(roleId);
    if (it == roles_.end()) return false;
    return it->second.permissions.erase(permId) > 0;
}

// ---------- 权限检查 ----------
bool RbacEngine::hasPermission(const UserId& userId,
                               const PermissionId& permissionId) const {
    auto uIt = users_.find(userId);
    if (uIt == users_.end()) return false;
    for (const auto& roleId : uIt->second.roles) {
        auto rIt = roles_.find(roleId);
        if (rIt != roles_.end() && rIt->second.permissions.count(permissionId))
            return true;
    }
    return false;
}

bool RbacEngine::hasAllPermissions(
    const UserId& userId,
    const std::vector<PermissionId>& permissionIds) const {
    for (const auto& pid : permissionIds)
        if (!hasPermission(userId, pid)) return false;
    return true;
}

bool RbacEngine::hasAnyPermission(
    const UserId& userId,
    const std::vector<PermissionId>& permissionIds) const {
    for (const auto& pid : permissionIds)
        if (hasPermission(userId, pid)) return true;
    return false;
}

// ---------- 查询 ----------
std::vector<RoleId> RbacEngine::getRolesForUser(const UserId& userId) const {
    auto it = users_.find(userId);
    if (it == users_.end()) return {};
    std::vector<RoleId> result(it->second.roles.begin(), it->second.roles.end());
    return result;
}

std::vector<PermissionId> RbacEngine::getPermissionsForUser(
    const UserId& userId) const {
    std::unordered_set<PermissionId> out;
    for (const auto& roleId : getRolesForUser(userId)) {
        auto rIt = roles_.find(roleId);
        if (rIt != roles_.end())
            for (const auto& p : rIt->second.permissions) out.insert(p);
    }
    return std::vector<PermissionId>(out.begin(), out.end());
}

std::vector<PermissionId> RbacEngine::getPermissionsForRole(
    const RoleId& roleId) const {
    auto it = roles_.find(roleId);
    if (it == roles_.end()) return {};
    return std::vector<PermissionId>(it->second.permissions.begin(),
                                     it->second.permissions.end());
}

}  // namespace rbac

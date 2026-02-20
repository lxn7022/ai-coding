/**
 * RbacEngine 核心逻辑单元测试
 */
#include "rbac/rbac_engine.hpp"
#include <gtest/gtest.h>
#include <set>
#include <string>

using namespace rbac;

// ---------- 用户 ----------
TEST(RbacEngine, AddUser_Success) {
    RbacEngine e;
    EXPECT_TRUE(e.addUser("u1", "Alice"));
    auto u = e.getUser("u1");
    ASSERT_TRUE(u.has_value());
    EXPECT_EQ(u->id, "u1");
    EXPECT_EQ(u->name, "Alice");
    EXPECT_TRUE(u->roles.empty());
}

TEST(RbacEngine, AddUser_Duplicate_ReturnsFalse) {
    RbacEngine e;
    EXPECT_TRUE(e.addUser("u1", "Alice"));
    EXPECT_FALSE(e.addUser("u1", "Bob"));
    EXPECT_EQ(e.getUser("u1")->name, "Alice");
}

TEST(RbacEngine, RemoveUser_Existing) {
    RbacEngine e;
    e.addUser("u1", "Alice");
    EXPECT_TRUE(e.removeUser("u1"));
    EXPECT_FALSE(e.getUser("u1").has_value());
}

TEST(RbacEngine, RemoveUser_NonExisting_ReturnsFalse) {
    RbacEngine e;
    EXPECT_FALSE(e.removeUser("none"));
}

TEST(RbacEngine, ListUsers) {
    RbacEngine e;
    e.addUser("u1", "A");
    e.addUser("u2", "B");
    auto list = e.listUsers();
    EXPECT_EQ(list.size(), 2u);
    std::set<std::string> ids;
    for (const auto& u : list) ids.insert(u.id);
    EXPECT_TRUE(ids.count("u1"));
    EXPECT_TRUE(ids.count("u2"));
}

// ---------- 角色 ----------
TEST(RbacEngine, AddRole_Success) {
    RbacEngine e;
    EXPECT_TRUE(e.addRole("r1", "Admin", "管理员"));
    auto r = e.getRole("r1");
    ASSERT_TRUE(r.has_value());
    EXPECT_EQ(r->id, "r1");
    EXPECT_EQ(r->name, "Admin");
    EXPECT_EQ(r->description, "管理员");
    EXPECT_TRUE(r->permissions.empty());
}

TEST(RbacEngine, AddRole_Duplicate_ReturnsFalse) {
    RbacEngine e;
    EXPECT_TRUE(e.addRole("r1", "Admin", ""));
    EXPECT_FALSE(e.addRole("r1", "Other", ""));
}

TEST(RbacEngine, RemoveRole_Existing) {
    RbacEngine e;
    e.addRole("r1", "Admin");
    EXPECT_TRUE(e.removeRole("r1"));
    EXPECT_FALSE(e.getRole("r1").has_value());
}

TEST(RbacEngine, RemoveRole_FromUserRoles) {
    RbacEngine e;
    e.addUser("u1", "A");
    e.addRole("r1", "R");
    e.assignRoleToUser("u1", "r1");
    e.removeRole("r1");
    EXPECT_FALSE(e.getRole("r1").has_value());
    auto roles = e.getRolesForUser("u1");
    EXPECT_TRUE(roles.empty());
}

// ---------- 权限 ----------
TEST(RbacEngine, AddPermission_Success) {
    RbacEngine e;
    EXPECT_TRUE(e.addPermission("p1", "Read", "读权限"));
    auto p = e.getPermission("p1");
    ASSERT_TRUE(p.has_value());
    EXPECT_EQ(p->id, "p1");
    EXPECT_EQ(p->name, "Read");
}

TEST(RbacEngine, AddPermission_EmptyName_UsesId) {
    RbacEngine e;
    e.addPermission("user:read", "", "");
    EXPECT_EQ(e.getPermission("user:read")->name, "user:read");
}

TEST(RbacEngine, RemovePermission_FromRoles) {
    RbacEngine e;
    e.addRole("r1", "R");
    e.assignPermissionToRole("r1", "p1");
    e.removePermission("p1");
    EXPECT_FALSE(e.getPermission("p1").has_value());
    auto perms = e.getPermissionsForRole("r1");
    EXPECT_TRUE(perms.empty());
}

// ---------- 分配：用户-角色 ----------
TEST(RbacEngine, AssignRoleToUser_Success) {
    RbacEngine e;
    e.addUser("u1", "A");
    e.addRole("r1", "R");
    EXPECT_TRUE(e.assignRoleToUser("u1", "r1"));
    auto roles = e.getRolesForUser("u1");
    EXPECT_EQ(roles.size(), 1u);
    EXPECT_EQ(roles[0], "r1");
}

TEST(RbacEngine, AssignRoleToUser_InvalidUser_ReturnsFalse) {
    RbacEngine e;
    e.addRole("r1", "R");
    EXPECT_FALSE(e.assignRoleToUser("none", "r1"));
}

TEST(RbacEngine, AssignRoleToUser_InvalidRole_ReturnsFalse) {
    RbacEngine e;
    e.addUser("u1", "A");
    EXPECT_FALSE(e.assignRoleToUser("u1", "none"));
}

TEST(RbacEngine, RevokeRoleFromUser_Success) {
    RbacEngine e;
    e.addUser("u1", "A");
    e.addRole("r1", "R");
    e.assignRoleToUser("u1", "r1");
    EXPECT_TRUE(e.revokeRoleFromUser("u1", "r1"));
    EXPECT_TRUE(e.getRolesForUser("u1").empty());
}

TEST(RbacEngine, RevokeRoleFromUser_NoSuchRole_ReturnsFalse) {
    RbacEngine e;
    e.addUser("u1", "A");
    EXPECT_FALSE(e.revokeRoleFromUser("u1", "r1"));
}

// ---------- 分配：角色-权限 ----------
TEST(RbacEngine, AssignPermissionToRole_Success) {
    RbacEngine e;
    e.addRole("r1", "R");
    EXPECT_TRUE(e.assignPermissionToRole("r1", "p1"));
    auto perms = e.getPermissionsForRole("r1");
    EXPECT_EQ(perms.size(), 1u);
    EXPECT_EQ(perms[0], "p1");
}

TEST(RbacEngine, RevokePermissionFromRole_Success) {
    RbacEngine e;
    e.addRole("r1", "R");
    e.assignPermissionToRole("r1", "p1");
    EXPECT_TRUE(e.revokePermissionFromRole("r1", "p1"));
    EXPECT_TRUE(e.getPermissionsForRole("r1").empty());
}

// ---------- 权限检查 ----------
TEST(RbacEngine, HasPermission_ThroughRole_True) {
    RbacEngine e;
    e.addUser("u1", "A");
    e.addRole("r1", "R");
    e.assignRoleToUser("u1", "r1");
    e.assignPermissionToRole("r1", "user:read");
    EXPECT_TRUE(e.hasPermission("u1", "user:read"));
}

TEST(RbacEngine, HasPermission_NoRole_False) {
    RbacEngine e;
    e.addUser("u1", "A");
    EXPECT_FALSE(e.hasPermission("u1", "user:read"));
}

TEST(RbacEngine, HasPermission_NoSuchUser_False) {
    RbacEngine e;
    EXPECT_FALSE(e.hasPermission("none", "user:read"));
}

TEST(RbacEngine, HasPermission_RoleWithoutPerm_False) {
    RbacEngine e;
    e.addUser("u1", "A");
    e.addRole("r1", "R");
    e.assignRoleToUser("u1", "r1");
    e.assignPermissionToRole("r1", "user:read");
    EXPECT_FALSE(e.hasPermission("u1", "user:write"));
}

TEST(RbacEngine, HasPermission_MultipleRoles_AnyHasPerm) {
    RbacEngine e;
    e.addUser("u1", "A");
    e.addRole("r1", "R1");
    e.addRole("r2", "R2");
    e.assignRoleToUser("u1", "r1");
    e.assignRoleToUser("u1", "r2");
    e.assignPermissionToRole("r2", "order:write");
    EXPECT_TRUE(e.hasPermission("u1", "order:write"));
}

TEST(RbacEngine, HasAllPermissions_Empty_True) {
    RbacEngine e;
    e.addUser("u1", "A");
    std::vector<PermissionId> empty;
    EXPECT_TRUE(e.hasAllPermissions("u1", empty));
}

TEST(RbacEngine, HasAllPermissions_AllGranted_True) {
    RbacEngine e;
    e.addUser("u1", "A");
    e.addRole("r1", "R");
    e.assignRoleToUser("u1", "r1");
    e.assignPermissionToRole("r1", "p1");
    e.assignPermissionToRole("r1", "p2");
    EXPECT_TRUE(e.hasAllPermissions("u1", {"p1", "p2"}));
}

TEST(RbacEngine, HasAllPermissions_OneMissing_False) {
    RbacEngine e;
    e.addUser("u1", "A");
    e.addRole("r1", "R");
    e.assignRoleToUser("u1", "r1");
    e.assignPermissionToRole("r1", "p1");
    EXPECT_FALSE(e.hasAllPermissions("u1", {"p1", "p2"}));
}

TEST(RbacEngine, HasAnyPermission_OneGranted_True) {
    RbacEngine e;
    e.addUser("u1", "A");
    e.addRole("r1", "R");
    e.assignRoleToUser("u1", "r1");
    e.assignPermissionToRole("r1", "p1");
    EXPECT_TRUE(e.hasAnyPermission("u1", {"p1", "p2"}));
}

TEST(RbacEngine, HasAnyPermission_NoneGranted_False) {
    RbacEngine e;
    e.addUser("u1", "A");
    e.addRole("r1", "R");
    e.assignRoleToUser("u1", "r1");
    EXPECT_FALSE(e.hasAnyPermission("u1", {"p1", "p2"}));
}

// ---------- 查询 ----------
TEST(RbacEngine, GetRolesForUser_NonExisting_Empty) {
    RbacEngine e;
    auto roles = e.getRolesForUser("none");
    EXPECT_TRUE(roles.empty());
}

TEST(RbacEngine, GetPermissionsForUser_AggregatesRoles) {
    RbacEngine e;
    e.addUser("u1", "A");
    e.addRole("r1", "R1");
    e.addRole("r2", "R2");
    e.assignRoleToUser("u1", "r1");
    e.assignRoleToUser("u1", "r2");
    e.assignPermissionToRole("r1", "p1");
    e.assignPermissionToRole("r2", "p2");
    auto perms = e.getPermissionsForUser("u1");
    EXPECT_EQ(perms.size(), 2u);
    std::set<std::string> set(perms.begin(), perms.end());
    EXPECT_TRUE(set.count("p1"));
    EXPECT_TRUE(set.count("p2"));
}

TEST(RbacEngine, GetPermissionsForRole_NonExisting_Empty) {
    RbacEngine e;
    auto perms = e.getPermissionsForRole("none");
    EXPECT_TRUE(perms.empty());
}

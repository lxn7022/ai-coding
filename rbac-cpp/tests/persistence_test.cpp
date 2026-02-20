/**
 * Persistence 持久化单元测试：保存与加载一致性
 */
#include "rbac/persistence.hpp"
#include "rbac/rbac_engine.hpp"
#include <gtest/gtest.h>
#include <cstdio>
#include <set>
#include <string>

using namespace rbac;

static std::string TempPath() {
#ifdef _WIN32
    return std::string("rbac_test_") + std::to_string(static_cast<unsigned>(time(nullptr)));
#else
    return "/tmp/rbac_test_" + std::to_string(static_cast<unsigned>(time(nullptr)));
#endif
}

TEST(Persistence, SaveLoad_RoundTrip) {
    RbacEngine orig;
    orig.addPermission("user:read", "读用户", "");
    orig.addPermission("user:write", "写用户", "");
    orig.addRole("admin", "管理员", "全部权限");
    orig.addRole("viewer", "只读", "仅查看");
    orig.assignPermissionToRole("admin", "user:read");
    orig.assignPermissionToRole("admin", "user:write");
    orig.assignPermissionToRole("viewer", "user:read");
    orig.addUser("u1", "Alice");
    orig.addUser("u2", "Bob");
    orig.assignRoleToUser("u1", "admin");
    orig.assignRoleToUser("u2", "viewer");

    const std::string path = TempPath();
    ASSERT_TRUE(Persistence::save(orig, path));

    RbacEngine loaded;
    ASSERT_TRUE(Persistence::load(loaded, path));
    std::remove(path.c_str());

    // 用户
    EXPECT_EQ(loaded.listUsers().size(), 2u);
    auto u1 = loaded.getUser("u1");
    ASSERT_TRUE(u1.has_value());
    EXPECT_EQ(u1->name, "Alice");
    auto roles1 = loaded.getRolesForUser("u1");
    EXPECT_EQ(roles1.size(), 1u);
    EXPECT_EQ(roles1[0], "admin");

    // 角色与权限
    EXPECT_EQ(loaded.listRoles().size(), 2u);
    EXPECT_TRUE(loaded.hasPermission("u1", "user:write"));
    EXPECT_TRUE(loaded.hasPermission("u2", "user:read"));
    EXPECT_FALSE(loaded.hasPermission("u2", "user:write"));
}

TEST(Persistence, Save_EmptyEngine) {
    RbacEngine e;
    const std::string path = TempPath();
    ASSERT_TRUE(Persistence::save(e, path));
    RbacEngine loaded;
    ASSERT_TRUE(Persistence::load(loaded, path));
    std::remove(path.c_str());
    EXPECT_TRUE(loaded.listUsers().empty());
    EXPECT_TRUE(loaded.listRoles().empty());
    EXPECT_TRUE(loaded.listPermissions().empty());
}

TEST(Persistence, Load_InvalidPath_ReturnsFalse) {
    RbacEngine e;
    EXPECT_FALSE(Persistence::load(e, "/nonexistent/path/rbac_xxx_12345"));
}

TEST(Persistence, Save_InvalidPath_ReturnsFalse) {
    RbacEngine e;
    e.addUser("u1", "A");
#ifdef _WIN32
    EXPECT_FALSE(Persistence::save(e, "Z:\\nonexistent\\rbac_xxx"));
#else
    EXPECT_FALSE(Persistence::save(e, "/nonexistent/rbac_xxx"));
#endif
}

TEST(Persistence, RoundTrip_SpecialCharsInNames) {
    RbacEngine orig;
    orig.addUser("u1", "Name\tWith\tTabs");
    orig.addRole("r1", "Role\nNewline", "Desc\\Backslash");
    orig.assignRoleToUser("u1", "r1");

    const std::string path = TempPath();
    ASSERT_TRUE(Persistence::save(orig, path));

    RbacEngine loaded;
    ASSERT_TRUE(Persistence::load(loaded, path));
    std::remove(path.c_str());

    auto u = loaded.getUser("u1");
    ASSERT_TRUE(u.has_value());
    EXPECT_EQ(u->name, "Name\tWith\tTabs");
    auto r = loaded.getRole("r1");
    ASSERT_TRUE(r.has_value());
    EXPECT_EQ(r->name, "Role\nNewline");
    EXPECT_EQ(r->description, "Desc\\Backslash");
    EXPECT_EQ(loaded.getRolesForUser("u1").size(), 1u);
}

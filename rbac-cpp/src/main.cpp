/**
 * RBAC 权限管理系统 - 示例程序
 * 演示：创建用户/角色/权限、分配关系、权限检查、持久化
 */
#include "rbac/persistence.hpp"
#include "rbac/rbac_engine.hpp"
#include <iostream>
#if defined(_WIN32)
#include <windows.h>
#endif

using namespace rbac;

static void printSep() { std::cout << "---\n"; }

int main() {
#if defined(_WIN32)
    // 控制台使用 UTF-8，避免中文乱码
    SetConsoleOutputCP(65001);
    SetConsoleCP(65001);
#endif
    RbacEngine engine;

    // 1. 定义权限（资源:操作）
    engine.addPermission("user:read", "查看用户", "查看用户列表与详情");
    engine.addPermission("user:write", "编辑用户", "创建/修改/删除用户");
    engine.addPermission("order:read", "查看订单", "查看订单列表与详情");
    engine.addPermission("order:write", "编辑订单", "创建/修改/取消订单");
    engine.addPermission("admin:all", "超级管理", "所有管理权限");

    // 2. 定义角色
    engine.addRole("admin", "管理员", "系统管理员，拥有全部权限");
    engine.addRole("operator", "运营", "订单与用户日常操作");
    engine.addRole("viewer", "只读", "仅查看");

    // 3. 为角色分配权限
    engine.assignPermissionToRole("admin", "admin:all");
    engine.assignPermissionToRole("operator", "user:read");
    engine.assignPermissionToRole("operator", "user:write");
    engine.assignPermissionToRole("operator", "order:read");
    engine.assignPermissionToRole("operator", "order:write");
    engine.assignPermissionToRole("viewer", "user:read");
    engine.assignPermissionToRole("viewer", "order:read");

    // 4. 创建用户并分配角色
    engine.addUser("u1", "张三");
    engine.addUser("u2", "李四");
    engine.addUser("u3", "王五");
    engine.assignRoleToUser("u1", "admin");
    engine.assignRoleToUser("u2", "operator");
    engine.assignRoleToUser("u3", "viewer");

    // 5. 权限检查演示
    std::cout << "=== 权限检查 ===\n";
    auto check = [&engine](const UserId& uid, const PermissionId& perm) {
        bool ok = engine.hasPermission(uid, perm);
        std::cout << "  用户 " << uid << " 拥有 " << perm << " ? " << (ok ? "是" : "否") << "\n";
    };
    check("u1", "admin:all");
    check("u1", "user:write");
    check("u2", "user:write");
    check("u2", "admin:all");
    check("u3", "order:read");
    check("u3", "order:write");
    printSep();

    // 6. 查询用户角色与权限
    std::cout << "=== 用户 u2 的角色 ===\n";
    for (const auto& rid : engine.getRolesForUser("u2"))
        std::cout << "  " << rid << "\n";
    std::cout << "用户 u2 的权限:\n";
    for (const auto& pid : engine.getPermissionsForUser("u2"))
        std::cout << "  " << pid << "\n";
    printSep();

    // 7. 持久化：保存到文件
    const std::string dataFile = "rbac_data.txt";
    if (Persistence::save(engine, dataFile))
        std::cout << "已保存到 " << dataFile << "\n";
    else
        std::cout << "保存失败\n";

    // 8. 从文件加载到新引擎并验证
    RbacEngine engine2;
    if (Persistence::load(engine2, dataFile)) {
        std::cout << "已从 " << dataFile << " 加载\n";
        std::cout << "加载后 u1 拥有 admin:all ? " << (engine2.hasPermission("u1", "admin:all") ? "是" : "否") << "\n";
    } else {
        std::cout << "加载失败\n";
    }

    return 0;
}

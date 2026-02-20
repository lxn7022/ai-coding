# RBAC 权限管理系统（C++）

基于 **RBAC（Role-Based Access Control）** 模型的 C++ 权限管理库与示例程序。

## 模型说明

- **用户（User）**：需要访问系统的主体。
- **角色（Role）**：岗位或职能，如「管理员」「运营」「只读」。
- **权限（Permission）**：对资源的操作，建议格式 `资源:操作`，如 `user:read`、`order:write`。
- **关系**：
  - 用户 ↔ 角色：多对多（一个用户可有多个角色）。
  - 角色 ↔ 权限：多对多（一个角色包含多个权限）。
- **判定**：用户是否拥有某权限 = 该用户是否拥有至少一个包含该权限的角色。

## 项目结构

```
include/rbac/
  types.hpp        # 用户、角色、权限等类型定义
  rbac_engine.hpp  # RBAC 引擎接口
  persistence.hpp  # 文件持久化接口
src/
  rbac_engine.cpp  # 引擎实现
  persistence.cpp  # 持久化实现
  main.cpp         # 示例程序
```

## 构建

需要 CMake 3.14+ 与支持 C++17 的编译器（如 MSVC 2017+、GCC 7+、Clang 5+）。

```bash
mkdir build && cd build
cmake ..
cmake --build .
```

Windows 下可用 Visual Studio 打开 `build` 目录或使用「从源代码打开」选择本目录并配置 CMake。

## 运行示例

```bash
./rbac_demo   # Linux/macOS
```

**Windows（Visual Studio 生成器）**：可执行文件在 `build\<配置>\rbac_demo.exe`，默认 Debug 时：

```powershell
.\build\Debug\rbac_demo.exe
```

Release 构建：`cmake --build . --config Release`，然后 `.\build\Release\rbac_demo.exe`。

示例会：创建用户/角色/权限、分配关系、做权限检查、将数据保存到 `rbac_data.txt` 并再次加载验证。

## API 概览

### 引擎 `rbac::RbacEngine`

- **用户**：`addUser(id, name)`、`removeUser(id)`、`getUser(id)`、`listUsers()`
- **角色**：`addRole(id, name, description)`、`removeRole(id)`、`getRole(id)`、`listRoles()`
- **权限**：`addPermission(id, name, description)`、`removePermission(id)`、`getPermission(id)`、`listPermissions()`
- **分配**：`assignRoleToUser(userId, roleId)`、`revokeRoleFromUser(userId, roleId)`  
  `assignPermissionToRole(roleId, permId)`、`revokePermissionFromRole(roleId, permId)`
- **检查**：`hasPermission(userId, permissionId)`、`hasAllPermissions(userId, ids)`、`hasAnyPermission(userId, ids)`
- **查询**：`getRolesForUser(userId)`、`getPermissionsForUser(userId)`、`getPermissionsForRole(roleId)`

### 持久化 `rbac::Persistence`

- `save(engine, filepath)`：将当前引擎状态保存到文本文件。
- `load(engine, filepath)`：从文件加载，会覆盖当前引擎内容。

持久化文件为 Tab 分隔的纯文本，便于查看与版本管理。

## 使用示例

```cpp
#include "rbac/rbac_engine.hpp"

rbac::RbacEngine engine;
engine.addPermission("user:read", "查看用户", "");
engine.addRole("admin", "管理员", "");
engine.assignPermissionToRole("admin", "user:read");
engine.addUser("alice", "Alice");
engine.assignRoleToUser("alice", "admin");

if (engine.hasPermission("alice", "user:read")) {
    // 允许访问
}
```

## 许可证

可按项目需求自行选择许可证。

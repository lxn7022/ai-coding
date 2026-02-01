# RBAC 权限管理系统

基于 **RBAC（Role-Based Access Control）** 模型的 Python 权限管理系统，使用 FastAPI + SQLAlchemy + SQLite 实现。

## 功能概览

- **用户管理**：用户 CRUD、分配角色
- **角色管理**：角色 CRUD、为角色绑定权限
- **权限管理**：权限 CRUD，支持资源/操作维度（如 `user:create`）
- **认证**：登录获取 JWT，接口按权限校验（需权限码如 `user:read`）

## 项目结构

```
rbac2/
├── app/
│   ├── __init__.py
│   ├── config.py          # 配置
│   ├── database.py        # 数据库连接与会话
│   ├── auth.py            # 认证、JWT、权限校验依赖
│   ├── main.py            # FastAPI 入口
│   ├── models/            # SQLAlchemy 模型
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── permission.py
│   │   └── association.py  # 用户-角色、角色-权限关联表
│   ├── schemas/           # Pydantic 请求/响应模型
│   ├── services/          # 业务逻辑
│   └── api/               # 路由
│       ├── auth.py        # 登录、当前用户
│       ├── users.py
│       ├── roles.py
│       └── permissions.py
├── scripts/
│   └── seed.py            # 初始化权限、角色、管理员
├── requirements.txt
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
cd rbac2
pip install -r requirements.txt
```

### 2. 初始化数据（权限、角色、管理员）

```bash
python scripts/seed.py
```

将创建：

- 若干权限（如 `user:read`, `user:create`, `role:create` 等）
- 角色：`admin`（全部权限）、`user`（仅读）
- 管理员用户：**admin** / **admin123**

### 3. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API 文档：<http://localhost:8000/docs>
- 健康检查：<http://localhost:8000/api/health>

### 4. 使用流程

1. **登录**：`POST /api/auth/login`，Body: `{"username":"admin","password":"admin123"}`，得到 `access_token`。
2. **调用需权限接口**：在请求头加 `Authorization: Bearer <access_token>`。
3. 用户管理、角色管理、权限管理接口均需对应权限码（见下方权限说明）。

## RBAC 模型说明

- **User（用户）** ↔ **Role（角色）**：多对多，一个用户可有多个角色。
- **Role（角色）** ↔ **Permission（权限）**：多对多，一个角色可有多个权限。
- 用户实际权限 = 其所有角色下权限的并集。
- 权限以 **code** 标识，如 `user:create`、`role:read`，接口通过 `require_permissions("user:read")` 等做校验。

## 主要接口与所需权限

| 接口 | 所需权限（满足其一即可） |
|------|--------------------------|
| 用户列表/详情 | `user:read` 或 `user:list` |
| 创建用户 | `user:create` |
| 更新用户 | `user:update` |
| 删除用户 | `user:delete` |
| 为用户分配角色 | `user:assign_roles` 或 `role:assign` |
| 角色列表/详情 | `role:read` 或 `role:list` |
| 创建/更新/删除角色 | `role:create` / `role:update` / `role:delete` |
| 权限列表/详情 | `permission:read` 或 `permission:list` |
| 创建/更新/删除权限 | `permission:create` / `permission:update` / `permission:delete` |

## 配置

可通过环境变量或 `.env` 覆盖默认配置（见 `app/config.py`）：

- `DATABASE_URL`：数据库连接，默认 `sqlite:///./rbac.db`
- `SECRET_KEY`：JWT 密钥，生产环境务必修改
- `ACCESS_TOKEN_EXPIRE_MINUTES`：Token 过期时间（分钟）

## 扩展建议

- 将 SQLite 换为 PostgreSQL/MySQL：修改 `DATABASE_URL` 并安装对应驱动。
- 新增业务接口时，在路由上使用 `Depends(require_permissions("xxx:yyy"))` 做权限控制。
- 需要“必须同时具备多个权限”时，使用 `require_all_permissions("p1", "p2")`。

## License

MIT

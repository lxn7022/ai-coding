# RBAC 权限管理系统

基于 RBAC（Role-Based Access Control，基于角色的访问控制）模型的权限管理系统，使用 Go 语言开发。

## 技术栈

- **Web框架**: Gin
- **ORM**: GORM
- **数据库**: SQLite（可扩展为 MySQL/PostgreSQL）
- **认证**: JWT
- **密码加密**: bcrypt

## RBAC 模型说明

```
用户(User) <--多对多--> 角色(Role) <--多对多--> 权限(Permission)
```

- **用户(User)**: 系统使用者
- **角色(Role)**: 权限的集合，如管理员、普通用户等
- **权限(Permission)**: 对资源的操作权限，如查看用户、创建角色等

## 项目结构

```
rbac-golang/
├── main.go              # 程序入口
├── go.mod               # Go模块依赖
├── config/              # 配置
│   └── config.go
├── models/              # 数据模型
│   ├── base.go
│   ├── user.go
│   ├── role.go
│   └── permission.go
├── database/            # 数据库
│   └── db.go
├── handlers/            # API处理器
│   ├── response.go
│   ├── auth.go
│   ├── user.go
│   ├── role.go
│   └── permission.go
├── middleware/          # 中间件
│   ├── auth.go
│   └── cors.go
├── routes/              # 路由
│   └── routes.go
└── README.md
```

## 快速开始

### 安装依赖

```bash
go mod tidy
```

### 运行项目

```bash
go run main.go
```

服务启动后监听 `http://localhost:8080`

### 默认账号

- 用户名: `admin`
- 密码: `admin123`

## API 接口

### 认证接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | /api/v1/login | 用户登录 | 公开 |
| GET | /api/v1/me | 获取当前用户信息 | 登录 |
| PUT | /api/v1/me/password | 修改密码 | 登录 |

### 用户管理

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/v1/users | 获取用户列表 | user:list |
| GET | /api/v1/users/:id | 获取单个用户 | user:list |
| POST | /api/v1/users | 创建用户 | user:create |
| PUT | /api/v1/users/:id | 更新用户 | user:update |
| DELETE | /api/v1/users/:id | 删除用户 | user:delete |
| PUT | /api/v1/users/:id/roles | 分配角色 | user:update |
| GET | /api/v1/users/:id/roles | 获取用户角色 | user:list |
| GET | /api/v1/users/:id/permissions | 获取用户权限 | user:list |
| PUT | /api/v1/users/:id/password | 重置密码 | user:update |

### 角色管理

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/v1/roles | 获取角色列表 | role:list |
| GET | /api/v1/roles/all | 获取所有角色 | role:list |
| GET | /api/v1/roles/:id | 获取单个角色 | role:list |
| POST | /api/v1/roles | 创建角色 | role:create |
| PUT | /api/v1/roles/:id | 更新角色 | role:update |
| DELETE | /api/v1/roles/:id | 删除角色 | role:delete |
| PUT | /api/v1/roles/:id/permissions | 分配权限 | role:update |
| GET | /api/v1/roles/:id/permissions | 获取角色权限 | role:list |

### 权限管理

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/v1/permissions | 获取权限列表 | permission:list |
| GET | /api/v1/permissions/all | 获取所有权限 | permission:list |
| GET | /api/v1/permissions/tree | 获取权限树 | permission:list |
| GET | /api/v1/permissions/:id | 获取单个权限 | permission:list |
| POST | /api/v1/permissions | 创建权限 | permission:create |
| PUT | /api/v1/permissions/:id | 更新权限 | permission:update |
| DELETE | /api/v1/permissions/:id | 删除权限 | permission:delete |

## 使用示例

### 1. 登录获取 Token

```bash
curl -X POST http://localhost:8080/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

响应:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "nickname": "系统管理员",
      "status": 1,
      "roles": [...]
    }
  }
}
```

### 2. 使用 Token 访问接口

```bash
curl -X GET http://localhost:8080/api/v1/users \
  -H "Authorization: Bearer <your_token>"
```

### 3. 创建用户

```bash
curl -X POST http://localhost:8080/api/v1/users \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "123456",
    "email": "test@example.com",
    "nickname": "测试用户"
  }'
```

### 4. 给用户分配角色

```bash
curl -X PUT http://localhost:8080/api/v1/users/2/roles \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"role_ids": [2]}'
```

## 环境变量配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| SERVER_PORT | 服务端口 | 8080 |
| GIN_MODE | Gin运行模式 | debug |
| DB_DRIVER | 数据库驱动 | sqlite |
| DB_DSN | 数据库连接 | rbac.db |
| JWT_SECRET | JWT密钥 | rbac-secret-key-change-in-production |

## 功能特性

- [x] 用户管理（增删改查）
- [x] 角色管理（增删改查）
- [x] 权限管理（增删改查、树形结构）
- [x] 用户-角色关联
- [x] 角色-权限关联
- [x] JWT 认证
- [x] 权限中间件（基于权限码的访问控制）
- [x] 角色中间件（基于角色的访问控制）
- [x] 密码加密存储
- [x] 分页查询
- [x] 跨域支持

## License

MIT

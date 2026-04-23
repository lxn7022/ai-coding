---
name: FastAPI学生管理一表版
overview: 构建一个基于 FastAPI + SQLite 的学生信息管理系统，使用单表完成基础 CRUD，并突出请求校验、错误处理与文档化能力。
todos:
  - id: schema-design
    content: 定义 students 单表字段、唯一约束和初始化逻辑
    status: completed
  - id: pydantic-models
    content: 设计 StudentCreate/Update/Out 模型并加入字段校验
    status: completed
  - id: api-crud
    content: 实现 students 的创建、查询、列表、更新、删除接口及错误处理
    status: completed
  - id: docs-and-verify
    content: 补充 spec.md 文档并给出启动与接口验证步骤
    status: completed
isProject: false
---

# FastAPI 学生信息管理系统计划

## 目标与范围

- 在现有 FastAPI 示例基础上，实现一个“单表版学生管理系统”，用于演示 FastAPI 在参数校验、CRUD 接口、自动文档方面的常见用法。
- 数据库使用 SQLite，本地文件即可运行，无需额外数据库服务。
- 仅保留一张 `students` 表，满足新增、查询、修改、删除、列表检索。

## 实施方案

1. **定义单表结构与约束**
  - 在代码中定义 `students` 表字段：`id`（主键自增）、`student_no`（学号，唯一）、`name`、`age`、`gender`、`major`、`created_at`。
  - 添加必要约束（如年龄范围、学号唯一）以体现后端数据有效性控制。
2. **设计 Pydantic 请求/响应模型**
  - 新增 `StudentCreate`、`StudentUpdate`、`StudentOut` 模型。
  - 在模型中使用字段校验（例如 `age` 范围、字符串长度），展示 FastAPI 自动校验和错误返回。
3. **实现 CRUD 与查询接口**
  - `POST /students`：创建学生。
  - `GET /students/{id}`：按 ID 查询。
  - `GET /students`：分页列表（`skip`/`limit`）+ 可选按姓名关键词过滤。
  - `PUT /students/{id}`：更新学生信息。
  - `DELETE /students/{id}`：删除学生。
  - 统一处理未找到记录（404）与学号冲突（409）。
4. **完善启动与初始化逻辑**
  - 在应用启动时自动初始化数据库和表结构，保证首次启动可直接使用。
  - 保留根路由用于健康检查（如 `{"status": "ok"}`）。
5. **补充说明文档与验证步骤**
  - 在 `[/root/ai-coding/fastapi/spec.md](/root/ai-coding/fastapi/spec.md)` 写明：功能说明、表结构、接口示例、启动命令与测试步骤。
  - 提供 Swagger 文档访问方式（`/docs`）和最小验证流程（创建->查询->修改->删除）。

## 验证方式

- 启动服务后访问 `/docs`，逐条测试 CRUD 接口。
- 至少验证以下场景：
  - 正常新增和查询。
  - 学号重复触发冲突错误。
  - 非法年龄触发参数校验错误。
  - 删除后再次查询返回 404。


## 项目结构

```text
fastapi/
├── app/
│   ├── main.py                  # FastAPI 应用入口、路由注册
│   ├── schemas.py               # Pydantic 请求/响应模型
│   ├── routers/
│   │   └── students.py          # /students 相关接口
│   ├── db/
│   │   ├── database.py          # SQLite 连接、初始化、依赖注入
│   │   ├── crud.py              # 对 students 表的增删改查
│   │   ├── models.py            # 数据库表模型（students）
│   │   └── students.db          # SQLite 数据库文件（运行后生成）
│   └── tests/
│       ├── conftest.py          # 测试路径与环境初始化
│       └── test_students.py     # CRUD 与异常场景测试
├── main.py                  # 兼容入口（导出 app.main:app）
├── spec.md                  # 功能说明 + 接口说明 + 启动测试步骤
└── requirements.txt         # fastapi, uvicorn, sqlalchemy, pydantic
```

## 表定义

```text
CREATE TABLE students (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    student_no  VARCHAR(20) NOT NULL UNIQUE,
    name        VARCHAR(50) NOT NULL,
    age         INTEGER NOT NULL CHECK (age >= 1 AND age <= 120),
    gender      VARCHAR(10) NOT NULL CHECK (gender IN ('male', 'female', 'other')),
    major       VARCHAR(100) NOT NULL,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```


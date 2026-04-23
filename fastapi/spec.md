# FastAPI 学生信息管理系统（单表版）规范

## 1. 目标

构建一个简单的学生信息管理系统，用于演示 FastAPI 的常见用法：

- 路由与参数处理
- Pydantic 数据校验
- 基础 CRUD 接口
- 自动生成接口文档（`/docs`）

约束：仅使用一张数据库表（`students`）完成系统功能。

## 2. 推荐目录结构

```text
fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口、路由注册
│   ├── database.py          # SQLite 连接、初始化、依赖注入
│   ├── models.py            # 数据库表模型（students）
│   ├── schemas.py           # Pydantic 请求/响应模型
│   ├── crud.py              # 对 students 表的增删改查
│   └── routers/
│       ├── __init__.py
│       └── students.py      # /students 相关接口
├── spec.md                  # 功能说明 + 接口说明 + 启动测试步骤
├── requirements.txt         # fastapi, uvicorn, sqlalchemy, pydantic
└── students.db              # SQLite 数据库文件（运行后生成）
```

## 3. 分层职责

- `app/routers/students.py`
  - 处理 HTTP 请求与响应
  - 参数接收与状态码定义
  - 统一异常映射（如 404、409）

- `app/schemas.py`
  - 定义请求/响应模型
  - 通过 Pydantic 做字段校验
  - 示例：`StudentCreate`、`StudentUpdate`、`StudentOut`

- `app/crud.py`
  - 封装数据库操作逻辑
  - 提供 `create/get/list/update/delete` 方法

- `app/models.py`
  - 定义数据库模型（仅 `students`）
  - 维护字段约束（如 `student_no` 唯一）

- `app/database.py`
  - 数据库连接与 Session 管理
  - 初始化表结构
  - 提供 `get_db` 依赖注入

- `app/main.py`
  - 创建 FastAPI 应用
  - 注册路由
  - 挂载健康检查接口

## 4. 单表设计（students）

建议字段如下：

- `id`：主键，自增
- `student_no`：学号，唯一
- `name`：姓名
- `age`：年龄
- `gender`：性别
- `major`：专业
- `created_at`：创建时间

## 5. API 设计

- `GET /`
  - 健康检查

- `POST /students`
  - 创建学生信息

- `GET /students/{id}`
  - 根据 ID 查询学生

- `GET /students`
  - 学生列表查询
  - 支持分页参数：`skip`、`limit`
  - 支持可选姓名关键词过滤：`name`

- `PUT /students/{id}`
  - 更新学生信息

- `DELETE /students/{id}`
  - 删除学生信息

## 6. 错误处理约定

- 学生不存在：返回 `404`
- 学号重复：返回 `409`
- 请求参数不合法（如年龄越界）：返回 `422`

## 7. 运行与验证

### 7.1 启动

```bash
fastapi dev app/main.py
```

或：

```bash
uvicorn app.main:app --reload
```

### 7.2 验证步骤

1. 访问 `http://127.0.0.1:8000/docs`
2. 按顺序测试：
   - 创建学生（POST）
   - 查询学生（GET by id）
   - 列表查询（GET list）
   - 修改学生（PUT）
   - 删除学生（DELETE）
3. 验证异常场景：
   - 重复 `student_no` 触发 `409`
   - 非法 `age` 触发 `422`
   - 删除后查询触发 `404`

```bash
# 终端1：启动服务
conda activate fastapi-env
cd /root/ai-coding/fastapi
fastapi dev app/main.py

# 终端2：执行联调清单
cd /root/ai-coding/fastapi
./app/tests/smoke_curl.sh
```

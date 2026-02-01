"""RBAC 权限管理系统 - FastAPI 入口"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.api import auth, users, roles, permissions


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时创建表；关闭时无额外清理"""
    init_db()
    yield


app = FastAPI(
    title="RBAC 权限管理系统",
    description="基于 RBAC 模型的用户、角色、权限管理 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(roles.router, prefix="/api")
app.include_router(permissions.router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "RBAC 权限管理系统",
        "docs": "/docs",
        "api": "/api",
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}

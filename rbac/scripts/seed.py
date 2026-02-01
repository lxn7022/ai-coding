"""初始化 RBAC 数据：权限、角色、管理员用户"""
import sys
from pathlib import Path

# 将项目根目录加入 path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import init_db, get_db_context
from app.models import User, Role, Permission
from app.auth import get_password_hash


def seed():
    init_db()
    with get_db_context() as db:
        # 1. 权限
        perms_data = [
            ("user:list", "用户列表", "user", "list", "查看用户列表"),
            ("user:read", "用户查看", "user", "read", "查看用户详情"),
            ("user:create", "用户创建", "user", "create", "创建用户"),
            ("user:update", "用户更新", "user", "update", "更新用户"),
            ("user:delete", "用户删除", "user", "delete", "删除用户"),
            ("user:assign_roles", "分配用户角色", "user", "assign_roles", "为用户分配角色"),
            ("role:list", "角色列表", "role", "list", "查看角色列表"),
            ("role:read", "角色查看", "role", "read", "查看角色详情"),
            ("role:create", "角色创建", "role", "create", "创建角色"),
            ("role:update", "角色更新", "role", "update", "更新角色"),
            ("role:delete", "角色删除", "role", "delete", "删除角色"),
            ("role:assign", "分配角色", "role", "assign", "分配角色给用户"),
            ("permission:list", "权限列表", "permission", "list", "查看权限列表"),
            ("permission:read", "权限查看", "permission", "read", "查看权限详情"),
            ("permission:create", "权限创建", "permission", "create", "创建权限"),
            ("permission:update", "权限更新", "permission", "update", "更新权限"),
            ("permission:delete", "权限删除", "permission", "delete", "删除权限"),
        ]
        for code, name, resource, action, desc in perms_data:
            if db.query(Permission).filter(Permission.code == code).first():
                continue
            db.add(Permission(code=code, name=name, resource=resource, action=action, description=desc))
        db.flush()

        # 2. 角色：管理员拥有全部权限，普通用户只有读
        admin_role = db.query(Role).filter(Role.code == "admin").first()
        if not admin_role:
            all_perms = db.query(Permission).all()
            admin_role = Role(code="admin", name="管理员", description="系统管理员，拥有全部权限")
            admin_role.permissions = all_perms
            db.add(admin_role)
            db.flush()

        user_role = db.query(Role).filter(Role.code == "user").first()
        if not user_role:
            read_perms = db.query(Permission).filter(
                Permission.code.in_(["user:list", "user:read", "role:list", "role:read", "permission:list", "permission:read"])
            ).all()
            user_role = Role(code="user", name="普通用户", description="仅查看权限")
            user_role.permissions = read_perms
            db.add(user_role)
            db.flush()

        # 3. 管理员用户 admin / admin123
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                display_name="管理员",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
            )
            admin_user.roles = [admin_role]
            db.add(admin_user)

    print("Seed 完成：权限、角色(admin/user)、用户(admin/admin123) 已创建。")


if __name__ == "__main__":
    seed()

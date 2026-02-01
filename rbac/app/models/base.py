"""模型基类"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime


class BaseMixin:
    """通用字段混入"""
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


from sqlalchemy.orm import declarative_base
Base = declarative_base()

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import schemas
from . import models


def get_student(db: Session, student_id: int) -> models.Student | None:
    return db.get(models.Student, student_id)


def get_student_by_no(db: Session, student_no: str) -> models.Student | None:
    stmt = select(models.Student).where(models.Student.student_no == student_no)
    return db.execute(stmt).scalar_one_or_none()


def list_students(
    db: Session, skip: int = 0, limit: int = 10, name: str | None = None
) -> list[models.Student]:
    stmt = select(models.Student).order_by(models.Student.id).offset(skip).limit(limit)
    if name:
        stmt = stmt.where(models.Student.name.like(f"%{name}%"))
    return list(db.execute(stmt).scalars().all())


def create_student(db: Session, data: schemas.StudentCreate) -> models.Student:
    student = models.Student(**data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def update_student(
    db: Session, student: models.Student, data: schemas.StudentUpdate
) -> models.Student:
    for key, value in data.model_dump().items():
        setattr(student, key, value)
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def delete_student(db: Session, student: models.Student) -> None:
    db.delete(student)
    db.commit()

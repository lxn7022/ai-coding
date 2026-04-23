from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import schemas
from ..db import crud
from ..db.database import get_db

router = APIRouter(prefix="/students", tags=["students"])


@router.post("", response_model=schemas.StudentOut, status_code=status.HTTP_201_CREATED)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    exists = crud.get_student_by_no(db, student.student_no)
    if exists:
        raise HTTPException(status_code=409, detail="student_no already exists")
    try:
        return crud.create_student(db, student)
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail="student_no already exists") from exc


@router.get("/{student_id}", response_model=schemas.StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="student not found")
    return student


@router.get("", response_model=list[schemas.StudentOut])
def list_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: str | None = Query(None, min_length=1),
    db: Session = Depends(get_db),
):
    return crud.list_students(db, skip=skip, limit=limit, name=name)


@router.put("/{student_id}", response_model=schemas.StudentOut)
def update_student(
    student_id: int, student: schemas.StudentUpdate, db: Session = Depends(get_db)
):
    existing = crud.get_student(db, student_id)
    if not existing:
        raise HTTPException(status_code=404, detail="student not found")
    duplicated = crud.get_student_by_no(db, student.student_no)
    if duplicated and duplicated.id != student_id:
        raise HTTPException(status_code=409, detail="student_no already exists")
    try:
        return crud.update_student(db, existing, student)
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail="student_no already exists") from exc


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    existing = crud.get_student(db, student_id)
    if not existing:
        raise HTTPException(status_code=404, detail="student not found")
    crud.delete_student(db, existing)

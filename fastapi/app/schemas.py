from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StudentBase(BaseModel):
    student_no: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=1, le=120)
    gender: str = Field(pattern="^(male|female|other)$")
    major: str = Field(min_length=1, max_length=100)


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    student_no: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=1, le=120)
    gender: str = Field(pattern="^(male|female|other)$")
    major: str = Field(min_length=1, max_length=100)


class StudentOut(StudentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

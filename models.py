from base import Base_Model
from pydantic import BaseModel
from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlmodel import (
        Field, Session, SQLModel,
        create_engine, select,
        Relationship
)

class SignUp(BaseModel):
    name: str
    MatricNo: str
    password: str
    password2: str
    model_config = {"extra": "forbid"}


class Student(Base_Model, table=True):
    name: str = Field(index=True)
    MatricNo: str | None = Field(default=None, index=True)
    password: str


class Questions(Base_Model, table=True):
    value: str
    options: list["Choices"] = Relationship(back_populates="question", cascade_delete="all, delete")


class Choices(Base_Model, table=True):
    question_id: UUID  = Field(foreign_key='questions.id', ondelete="CASCADE")
    text: str
    percentage: int = 0
    vote_count: int = 0

    question: Questions = Relationship(back_populates="options")


class Vote(Base_Model, table=True):
    user_id: UUID = Field(foreign_key="student.id")
    question_id: UUID = Field(foreign_key="questions.id")
    choice_id: UUID = Field(foreign_key="choices.id")

    __table_args__ = (UniqueConstraint("user_id", "question_id"),)


class Admin(Base_Model, table=True):
    username: str
    password: str
    name: str


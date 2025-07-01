from pydantic import BaseModel

from sqlmodel import Field, Session, SQLModel, create_engine, select

class SignUp(BaseModel):
    name: str
    MatricNo: str
    password: str
    password2: str
    model_config = {"extra": "forbid"}


class Student(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    MatricNo: str | None = Field(default=None, index=True)
    password: str

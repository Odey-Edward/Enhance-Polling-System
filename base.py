from sqlmodel import SQLModel, Field
from sqlalchemy import TIMESTAMP, Column
from datetime import datetime, timezone
from uuid import uuid4
from pydantic import UUID4


def datetime_now() -> datetime:
    return datetime.now(timezone.utc)


class Base_Model(SQLModel):
    """The BaseModel class from which future classes will be derived"""
    id: UUID4 = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime_now)
    updated_at: datetime = Field(default_factory=datetime_now)

    class Config:
        arbitrary_types_allowed = True

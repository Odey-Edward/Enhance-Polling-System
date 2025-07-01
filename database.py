from sqlmodel import SQLModel, Session, create_engine

from fastapi import Depends

from typing import Annotated

DATABASE_URL = "postgresql:///polldb"
engine = create_engine(DATABASE_URL, echo=True)



def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

from sqlmodel import SQLModel, Session, create_engine

from fastapi import Depends

from typing import Annotated

#DATABASE_URL = "postgresql:///polldb"

DATABASE_URL = "postgresql://polldb_9abj_user:OGpUjzfW8UV0A25ewwUpjRPgs7D3HdpC@dpg-d1httf6r433s73bes0eg-a/polldb_9abj"
engine = create_engine(DATABASE_URL, echo=True)



def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

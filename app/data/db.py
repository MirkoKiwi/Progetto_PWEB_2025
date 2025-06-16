from sqlmodel import create_engine, SQLModel, Session, select
from typing import Annotated
from fastapi import Depends
import os
from faker import Faker
from app.config import config

# TODO: remember to import all the DB models here

from app.models.registration import Registration  # NOQA
from app.models.event import Event, EventForm
from app.models.user import User


sqlite_file_name = config.root_dir / "data/database.db" # data/database.db
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args, echo=True)


def init_database() -> None:
    ds_exists = os.path.isfile(sqlite_file_name)
    SQLModel.metadata.create_all(engine)
    if not ds_exists:
        f = Faker("it_IT")
        with Session(engine) as session:

            # Fake users table
            users = [
                User(username=f.user_name(),
                     name = f.name(),
                     email=f.email()
                    )
                for _ in range(10)
            ]
            # Commit users table to database
            session.add_all(users)
            session.commit()


            # Fake events table
            events = [
                Event(title=f.catch_phrase(),
                      description=f.text(), 
                      date=f.date_time_this_year(), 
                      location=f.city()
                     )
                for _ in range(10)
            ]
            # Commit events table to database
            session.add_all(events)
            session.commit()




def get_session():
    with Session(engine) as session:
        yield session   


SessionDep = Annotated[Session, Depends(get_session)]

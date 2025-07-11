from sqlalchemy import create_engine
from sqlalchemy.orm import Session, DeclarativeBase

engine = create_engine('sqlite:///tests/test.db', echo=True)
session_test = Session(engine)

class Base(DeclarativeBase):
    pass
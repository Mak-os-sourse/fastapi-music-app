from sqlalchemy import create_engine
from sqlalchemy.orm import *

engine = create_engine("sqlite:///data-base.db", echo=True)

session_db = Session(engine)

class Base(DeclarativeBase):
    pass
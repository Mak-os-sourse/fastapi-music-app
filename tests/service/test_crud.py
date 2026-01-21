import pytest

from tests.fake_db import session_test, engine_test
from tests.base import Base

from tests.crud.model import *

from src.crud import *

Base.metadata.drop_all(engine_test)
Base.metadata.create_all(engine_test)

@pytest.fixture()
def test_data():
    data = [{"username": "mak", "password": "12343gs24"}, {"username": "Oleg", "password": "12se24"},
                 {"username": "Dasha", "password": "12532fs4"}, {"username": "Nikita", "password": "32Jf322"},
                 {"username": "Oleg", "password": "fs32@2se24"}]

    for i in data:
        session_test.add(User(**i))

    yield data

    stmt = delete(User)
    session_test.execute(stmt)
    session_test.commit()

def test_add_data(test_data):
    result = db_add_data(session_test, User, username="Mykola", password="31fs1zof9d")

    assert result.username == "Mykola"
    assert result.password == "31fs1zof9d"

    assert session_test.get(User, result.id) is not None

def test_get_one_data(test_data):
    args = [{"id": 1},
            {"username": test_data[0]["username"]},
            {"username": test_data[0]["username"], "password": test_data[0]["password"]}]

    for i in args:
        result = db_get_data(session_test, User, **i)[0]

        assert result.username == test_data[0]["username"]
        assert result.password == test_data[0]["password"]

def test_get_many_data(test_data):
    args = [{"id": [1, 2, 3, 4, 5]}, {}]

    for i in args:
        result = db_get_data(session_test, User, **i)

        assert result != [] and len(result) != 0

def test_del_one_data(test_data):
    data = session_test.get(User, 1)

    result = db_delete_data(session_test, User, id=1)

    new_data = session_test.get(User, 1)

    assert data != new_data


def test_del_all_data(test_data):
    data = session_test.scalars(select(User))

    result = db_delete_data(session_test, User)

    new_data = session_test.scalars(select(User))

    assert data != new_data
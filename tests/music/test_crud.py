import pytest, datetime

from tests.fake_db import session_test, Base, engine
from src.music.crud import get_music
from src.music.models import Music

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

data = Music(title="Teen spirit", genre="rock", author_id=1, info="The music was created by Nirvana", listing=0, release_date=datetime.datetime.now().timestamp())
data_2 =  Music(title="Australia", genre="others", author_id=1, info="The music was created by n/a", listing=0, release_date=datetime.datetime.now().timestamp())
data_3 = Music(title="Come As You Are", genre="rock", author_id=1, info="The music was created by Nirvana", listing=0, release_date=datetime.datetime.now().timestamp())

session_test.add_all([data, data_2, data_3])
session_test.commit()
def start_test():
    @pytest.mark.parametrize("id, title, genre, author_id", [(None, "Teen spirit", None, None), (1, None, None, None)])
    def test_get_one_music(id, title, genre, author_id):
        result = get_music(session_test)
        print(result)
        assert get_music(session_test) == [data]

    @pytest.mark.parametrize("id, title, genre, author_id", [(None, None, None, 1), (None, None, "rock", None), (None, "Teen spirit", "others", None)])
    def test_det_many_music(id, title, genre, author_id):
        result = get_music(session_test)
        print(result)
        assert get_music(session_test) in [data, data_2, data_3]

    # session_test.delete(data)
    # session_test.delete(data_2)
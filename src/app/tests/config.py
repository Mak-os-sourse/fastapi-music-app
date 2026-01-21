import pyotp
from pathlib import Path

from src.app.config import settings

class Response:
    def __init__(self):
        self.headers = {}

class SettingsTest:
    BASE_PATH = "/api/v1"
    USER_PATH = BASE_PATH + "/user"
    MUSIC_PATH = BASE_PATH + "/music"
    USER_DATA_PATH = BASE_PATH + "/user-data"
    
    DB_URL = 'sqlite+aiosqlite:///src/app/tests/test.db'
    PATH_FILES = Path("src/app/tests/files/")
    
    BASE32 = pyotp.random_base32()
    
    RESPONSE = Response()

settings_test = SettingsTest()

settings.DB_URL = settings_test.DB_URL
"""settings.PATH_USER_IMAGE = Path()
settings.PATH_USER_MUSIC = Path()
settings.PATH_MUSIC_COVER = Path()
settings.BASE_DIR = settings_test.PATH_FILES"""
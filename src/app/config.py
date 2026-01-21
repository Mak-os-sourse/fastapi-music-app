from pathlib import Path

class PasswordConf:
    SALT = "12f98e"

class DBConf:
    DB_URL = "postgresql+asyncpg://root:1234567@localhost:5432/db"

class APIConf:
    NAMESPACE_USER = "user"
    
    PREFIX_API = "/api/v1"
    PREFIX_USER_API = f"{PREFIX_API}/user"
    PREFIX_MUSIC_API = f"{PREFIX_API}/music"
    PREFIX_ALBUM_API = f"{PREFIX_API}/album"
    PREFIX_USER_DATA = f"{PREFIX_API}/user-data"
    
    KEY_REFRESH_COOKIE = "token"
    
    STATUS_OK = {"status": "OK"}
    
    LENGTH_MUSIC = 15 # minuts
    
    MAX_LEN_ALBUM = 25

class StorageConf:
    BASE_DIR = Path("static/")
    
    PATH_IMAGE = Path(BASE_DIR / "api/image/")
    PATH_MUSIC = Path(BASE_DIR / "api/music/")
    
    PATH_USER_IMAGE = Path(PATH_IMAGE / "users")
    PATH_USER_MUSIC = Path(PATH_MUSIC / "users")
    PATH_MUSIC_COVER = Path(PATH_IMAGE / "music/cover")
    
    FORMAT_IMAGE = ["jpg", "jpeg", "png", "gif", "bmp", "webp", "avif"]
    FORMAT_MUSIC = ["wav", "raw", "mp3", "aac", "ogg",
                    "opus", "flac", "alac", "mpeg"]
    
    BASE_FORMAT_IMAGE = "png"
    BASE_FORMAT_MUSIC = "mp3"
    
    SCALE_IAMGE = 120

class EmailConf:
    SENDER = "mack43794@gmail.com"
    PASSWORD = "pwwu qyhw nqbf lglr"

class OTPConf:
    LEN_OTP_CODE = 4
    PREFIX_OTP = "opt-"
    LIFE_OTP_CODE = 120
    
class TokenConf:
    SECRET_KEY = "178h434ljk547"
    ALGORITHM = "HS256"
    EXP_DAYS_REFRESH = 30
    EXP_MINUTES_ACCESS = 15
    
class CacaheConf:
    CACHE_HOST = "127.0.0.1"
    CACHE_PORT = 6379
    PREFIX_CACHE_FUNC = 'cache_func'

    EXP_USER_CACHE = 3600
    
class Settings(APIConf, CacaheConf, DBConf, EmailConf,
               TokenConf, StorageConf, PasswordConf, OTPConf):    
    MIN_LEN_PASSWORD = 6
    MIN_LEN_USER_NAME = 4
    MIN_LEN_MUSIC_NAME = 5
    MAX_LEN_MUSIC_NAME = 20
    MAX_LEN_USER_NAME = 20
    MAX_LEN_INFO = 50
    
    MUSIC_GENRES = [
        # Популярные и современные
        "pop", "rock", "hip hop", "rap", "r&b",
        "electronic", "dance", "techno", "house",
        "country", "jazz", "blues", "classical",
        
        # Рок направления
        "alternative rock", "indie rock", "punk rock",
        "hard rock", "heavy metal", "progressive rock",
        "grunge", "post-rock", "shoegaze",
        
        # Электронная музыка
        "trance", "dubstep", "drum & bass", "ambient",
        "idm", "synthpop", "electropop", "future bass",
        
        # Танцевальные стили
        "disco", "funk", "soul", "reggae", "ska",
        "latino", "salsa", "bachata", "reggaeton",
        
        # Фолк и этническая музыка
        "folk", "world music", "ethnic", "traditional",
        
        # Классика и академическая музыка
        "baroque", "romantic", "opera", "chamber music",
        "symphonic", "choral", "avant-garde",
        
        # Региональные и национальные стили
        "k-pop", "j-pop", "europop", "afrobeats",
        "bossa nova", "flamenco", "tango",
        
        # Жанры по настроению/назначению
        "lo-fi", "chillout", "meditation", "background music",
        "film score", "video game music", "experimental",
        
        # Исторические и ретро стили
        "swing", "big band", "rockabilly", "doo-wop",
        
        # Христианская и духовная музыка
        "gospel", "christian rock", "religious music"
    ]
    
settings = Settings()
from src.app.api.v1.endpoints.base import Base
from src.app.config import settings

class UserAPI(Base):
    GET = settings.PREFIX_USER_API + "/get/{id}/"
    ME = settings.PREFIX_USER_API + "/me/"
    SEARCH = settings.PREFIX_USER_API + "/search/"
    UPDATE = settings.PREFIX_USER_API + "/data/update/"
    SET_IMAGE = settings.PREFIX_USER_API + "/add/image/"
    GET_IMAGE = settings.PREFIX_USER_API + "/get/image/{id}/"

    
from pydantic import BaseModel, Field, EmailStr, field_validator
from src.app.schemas.base import SearchData, valid_data

from src.app.config import settings

class UserResponseModel(BaseModel):
    id: int
    name: str
    username: str
    email: str
    info: str
    date_creation: int

class UserDataSearch(SearchData):
    field: str = None
    
    @field_validator("field")
    def valid_field(cls, value):
        return valid_data(value, ["username", "name"])

class UserDataUpdate(BaseModel):
    field: str
    
    @field_validator("field")
    def valid_field(cls, value):
        result = valid_data(value, ["name", "info"])
        name = result.get("name", "")
        info = result.get("info", "")
        
        if len(name) < settings.MIN_LEN_USER_NAME or len(name) > settings.MAX_LEN_USER_NAME:
            raise ValueError(f"The invalid field len must be the min - {settings.MIN_LEN_USER_NAME}, max - {settings.MAX_LEN_USER_NAME}")
        elif len(info) > settings.MAX_LEN_INFO:
            raise ValueError(f"The invalid field len must be the {settings.MAX_LEN_INFO}")
        else:
            return result

class UserDataLogin(BaseModel):
    field: str = None
    password: str = Field(min_length=settings.MIN_LEN_PASSWORD)
    
    @field_validator("field")
    def valid_field(cls, value):
        if len(value.split("@", -1)) == 2 and len(value.split("@")[1].split(".", -1)):
            return {"email": value}
        else:
            return {"username": value}
                
class UserDataRegist(BaseModel):
    name: str = Field(min_length=settings.MIN_LEN_USER_NAME)
    username: str = Field(min_length=settings.MIN_LEN_USER_NAME)
    email: EmailStr
    password: str = Field(min_length=settings.MIN_LEN_PASSWORD)
    
class VerifyCode(UserDataLogin):
    code: str
    base32: str

class GenCode(BaseModel):
    email: EmailStr

class UpdatePassword(BaseModel):
    code: str
    base32: str
    email: EmailStr
    new_password: str = Field(min_length=settings.MIN_LEN_PASSWORD)
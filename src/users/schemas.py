from pydantic import BaseModel, Field, EmailStr

class UserDataLogin(BaseModel):
    username: str = Field(min_length=5)
    password: str = Field(min_length=6)

class UserDataRegist(UserDataLogin):
    email: EmailStr
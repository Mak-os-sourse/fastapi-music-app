from pydantic import BaseModel, field_validator, Field

from src.app.schemas.base import SearchData, valid_data

class AddUserData(BaseModel):
    music: list[int]

class CreateUserData(BaseModel):
    title: str
    is_private: bool = Field(deafult=False)

class GetUserData(SearchData):
    field: str
    
    @field_validator("field")
    def valid_field(cls, value):
        return valid_data(value, ["id", "music_id", "artist"])
    
class SearchUserData(SearchData):
    field: str
    count_music: int = 50
    
    @field_validator("field")
    def valid_field(cls, value):
        return valid_data(value, ["title"])
    
class UpdateUserData(BaseModel):
    field: str
    
    @field_validator("field")
    def valid_field(cls, value):
        result = valid_data(value, ["title", "is_private"])
        is_private = result.get("is_private", "").lower()
        
        if is_private == "true":
            result["is_private"] = True
        elif is_private == "false":
            result["is_private"] = False
        else:
            raise ValueError
        return result
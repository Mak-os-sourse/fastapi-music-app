from pydantic import BaseModel, field_validator, Field

from src.app.schemas.base import SearchData, valid_data
from src.app.config import settings

class SetMusic(BaseModel):
    name: str = Field(min_length=settings.MIN_LEN_MUSIC_NAME, max_length=settings.MAX_LEN_MUSIC_NAME)
    genre: str
    info: str = Field(max_length=settings.MAX_LEN_INFO, default="")
    text: str = Field(max_length=settings.MAX_LEN_INFO, default="")
    is_private: bool = Field(default=False)

class SearchMusic(SearchData):
    field: str = None
    
    @field_validator("field")
    def valid_field(cls, value):
        return valid_data(value, ["name", "info"])

class UpdateMusicData(BaseModel):
    field: str
    
    @field_validator("field")
    def valid_field(cls, value):
        result = valid_data(value, ["name", "info", "is_private"])
        is_private = result.get("is_private", "").lower()
        
        if is_private == "true":
            result["is_private"] = True
        elif is_private == "false":
            result["is_private"] = False
        else:
            raise ValueError("The value must be bool type")
        return result
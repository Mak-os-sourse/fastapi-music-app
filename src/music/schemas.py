from pydantic import BaseModel, field_validator, Field
from src.music.models import Music

class MusicDataCreate(BaseModel):
    title: str = Field(max_length=25)
    genre: str
    info: str = Field(max_length=50)

class MusicDataChange(BaseModel):
    id: int
    title: str = Field(max_length=25, default=None)
    genre: str = None
    info: str = Field(max_length=50, default=None)

class MusicDataGet(BaseModel):
    limit: int = 10
    offset: int = 0
    """id: int = None
    title: str = Field(max_length=25, default=None)
    genre: str = None
    author_id: int = None
    release_date: int = None"""
    sorting: list[str] = None
    where: list[str] = []

    @field_validator("sorting")
    def check_sorting(cls, value):
        for i in value:
            sorting_field = i.split(":", 1)

            if len(sorting_field) == 2:
                reverse = sorting_field[1]
                field = sorting_field[0]

                if reverse.lower() != "true" and reverse.lower() != "false":
                    raise ValueError("reverse parameter error (must be true or false)")

                if field not in Music.__table__.columns:
                    raise ValueError("reverse field error")
            else:
                raise ValueError("error, the string must contain field:revers (str:bool)")

        return value

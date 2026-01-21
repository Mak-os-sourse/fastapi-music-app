from datetime import datetime, timezone

from src.app.crud.base import CRUD
from src.app.models.user import User
from src.app.service.security import hash_pw

class UserCRUD:
    def __init__(self):
        self.crud = CRUD(User)
        
    async def add(self, session, username: str, name: str, email: str, password: str) -> dict:
        return await self.crud.add_data(session, username=username.lower(),
                                        name=name.lower(), email=email.lower(),
                                        password=hash_pw(password), info="",
                                        otp_enable=True, date_creation=int(datetime.now(timezone.utc).timestamp()))
        
    async def get(self, session, offset: int = 0, limit: int = 10, **fields) -> list[dict]:
        where = []
        
        for key, value in fields.items():
            field = getattr(User, key)
            where.append(field == value)
        
        return await self.crud.get_data(session, where=where, offset=offset, limit=limit)
    
    async def search(self, session, sorting: list[tuple[object, bool]] = None, offset: int = 0, limit: int = 10, **fields) -> list[dict]:
        where = []
        
        for key, value in fields.items():
            field = getattr(User, key)
            data = ""
            for i in value:
                data += f"{i}%"
            where.append(field.like(data))
        
        return await self.crud.get_data(session, where=where, sorting=sorting, offset=offset, limit=limit)
    
    async def update(self, session, id: int, **fields):
        await self.crud.update_data(session, where=[User.id == id], **fields)
    
    async def delete(self, session, id: int):
        await self.crud.delete_data(session, id=id)

user_crud = UserCRUD()
import time

from src.app.service.security import hash_pw
from src.app.config import settings
from src.app.models.user import User

from src.app.tests.utils.session import add_fake_data, get_fake_data
from src.app.tests.fake import fake

class UserUtils:
    async def add(self, session, n = 1, otp_enable: bool = True, retrun_hash_pw: bool = True):
        source, data = self._create_users(n, otp_enable)
        users = await add_fake_data(session, User, source)
        
        if not retrun_hash_pw:
            for value, user in zip(data, users):
                user["password"] = value["password"]
        return users
        
    async def get(self, session, **where) -> dict | None:
        return await get_fake_data(session, User, **where)

    def fake_user(self, otp_enable: bool = True):
        return {"username": fake.user_name(), "name": fake.name(), "email":  fake.email(),
                    "password": fake.password(), "info": "", "otp_enable": int(otp_enable), "date_creation": int(time.time())}

    def _create_users(self, n: int, otp_enable: bool) -> list[dict, dict]:
        data, source = [], []
        for _ in range(n):
            user = self.fake_user(otp_enable)
            hash_user = user.copy()
            hash_user["password"] = hash_pw(user["password"])
            source.append(user)
            data.append(hash_user)
        return source, data    
            
user_utils = UserUtils()
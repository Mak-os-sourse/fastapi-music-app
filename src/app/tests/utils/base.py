from src.app.tests.models import Base

from src.app.tests.fake import fake

from src.app.tests.utils.session import add_fake_data, get_fake_data

class BaseUtils:
    async def add(self, session, n = 1):
        return await add_fake_data(session, Base, [self.fake_data() for _ in range(n)])
    
    async def get(self, session, **where):
        return await get_fake_data(session, Base, **where)
    
    def fake_data(self):
        return {"username": fake.user_name(), "password": fake.password()}

base_utils = BaseUtils()
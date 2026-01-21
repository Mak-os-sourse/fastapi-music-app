from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.app.config import settings

class DataBase:
    def __init__(self, db_url: str, echo: bool = False):
        self.engine = create_async_engine(db_url, echo=echo)
        self.Session = async_sessionmaker(self.engine)

    async def get_session(self):
        async with self.Session() as session:
            yield session
    
    async def metadata_create_all(self, base):
        async with self.engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all)
    
    async def metadata_drop_all(self, base):
        async with self.engine.begin() as conn:
            await conn.run_sync(base.metadata.drop_all)

db = DataBase(settings.DB_URL, echo=True)
from sqlalchemy import insert, select

from src.app.utils.args import jsonable_encoder

async def add_fake_data(session, table, data: list[dict]) -> list[dict]:
    result = []
    for value in data:
        stmt = await session.scalars(insert(table).values(**value).returning(table))
        result.append(jsonable_encoder(stmt.one()))
        await session.commit()
    return result

async def get_fake_data(session, table, **where):
    where_list = []
    for key in where.keys():
        where_list.append(getattr(table, key) == where[key])
        
    result = await session.scalars(select(table).where(*where_list))
    result = result.one_or_none()
    return jsonable_encoder(result) if result is not None else None
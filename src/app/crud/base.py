from sqlalchemy import insert, select, delete, update, asc, desc
from sqlalchemy.sql.elements import BinaryExpression
from src.app.utils.args import jsonable_encoder

class CRUD:
    def __init__(self, model):
        self.model = model

    async def add_data(self, session, **fields) -> dict:
        stmt = insert(self.model).values(**fields).returning(self.model)

        result = await session.scalars(stmt)
        result = result.one()
        
        data = jsonable_encoder(result)
        await session.commit()
        return data
          
    async def get_data(self, session,
                       where: list[BinaryExpression] = [],
                       sorting: list[tuple[object, bool]] = None,
                       offset: int = 0,
                       limit: int = 10,
                       ) -> list[dict]:
        if sorting is not None:
            sorting_fields = self._extract_sorting(sorting)

            stmt = select(self.model).order_by(*sorting_fields).where(*where).limit(limit).offset(offset)
        else:
            stmt = select(self.model).where(*where).limit(limit).offset(offset)

        result = await session.scalars(stmt)
        
        data = []

        for i in result.all():
            data.append(jsonable_encoder(i))

        return data

    async def update_data(self, session, where, **value):
        stmt = update(self.model).where(*where).values(**value)

        await session.execute(stmt)
        await session.commit()

    async def delete_data(self, session, where: list[BinaryExpression] = [], **fields):
        list_where = self._extract_fields(**fields)

        stmt = delete(self.model).where(*list_where, *where)

        await session.execute(stmt)
        await session.commit()

    def _extract_fields(self, **fields) -> list:
        list_where = []

        for key, value in fields.items():
            list_where.append(getattr(self.model, key) == value)

        return list_where

    def _extract_sorting(self, sorting: list[tuple[str, bool]]) -> list:
        sorting_fields = []

        for i in sorting:
            field = i[0]
            reverse = i[1]

            if reverse is True:
                sorting_fields.append(desc(field))
            if reverse is False:
                sorting_fields.append(asc(field))

        return sorting_fields

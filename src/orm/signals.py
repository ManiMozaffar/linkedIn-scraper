

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import TypedReturnsRows


class SignalMixin:

    async def _pre_save(
        self, db_session: AsyncSession, instance=None, **kwargs
    ):
        _instance = await self.pre_save(
            db_session, instance=instance, **kwargs
        )
        if _instance is not None:
            return _instance
        else:
            return instance

    async def _pre_update(
            self, db_session: AsyncSession, stmt=None, **kwargs
    ) -> TypedReturnsRows:
        _stmt = await self.pre_update(db_session, stmt=stmt, **kwargs)
        if _stmt is not None:
            return _stmt
        else:
            return stmt

    async def _pre_delete(
            self, db_session: AsyncSession, stmt=None, **kwargs
    ) -> TypedReturnsRows:
        _stmt = await self.pre_delete(db_session, stmt=stmt, **kwargs)
        if _stmt is not None:
            return _stmt
        else:
            return stmt

    async def pre_save(self, db_session: AsyncSession, **kwargs):
        pass

    async def pre_update(self, db_session: AsyncSession, stmt=None, **kwargs):
        pass

    async def pre_delete(self, db_session: AsyncSession, stmt=None, **kwargs):
        pass

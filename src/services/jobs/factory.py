from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from services.common import CRUD


class JobCrud(CRUD):
    verbose_name = "Jobs"

    async def pre_save_check(self, db_session: AsyncSession, data: dict):
        if await self.model.objects.get(
            db_session=db_session, name=data.get('name')
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not Accepted, job already exists"
            )

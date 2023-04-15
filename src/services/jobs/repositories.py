from services.common import CRUD
from .models import Job
from fastapi import Depends, APIRouter, Request
from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import (
    JobCreate, JobUpdate, JobOut, JobQuery, CustomPaginationQuery
)
from typing import Optional
from fastapi import HTTPException, status


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


router = APIRouter()


@router.post("", response_model=JobOut)
async def create_job(data: JobCreate, db: AsyncSession = Depends(get_db)):
    data: dict = data.dict()
    return await JobCrud(
        Job, JobCreate, JobUpdate, JobCrud.verbose_name
    ).create(db, data=data)


@router.get("", response_model=None)
async def get_jobs(
        request: Request,
        data: JobQuery = Depends(),
        db: AsyncSession = Depends(get_db),
        paginated_data: CustomPaginationQuery = Depends(),
        order_by: Optional[str] = None
):
    paginated_data: dict = paginated_data.dict(exclude_unset=True)
    query_params: dict = data.dict(exclude_unset=True, exclude_defaults=True)
    data: dict = query_params.copy()
    query_params.update(paginated_data)
    base_url = str(request.url_for(request.scope["endpoint"].__name__)).rstrip("/")
    return await JobCrud(
            Job, JobCreate, JobUpdate, JobCrud.verbose_name
        ).paginated_read_all(
            db,
            order_by=order_by,
            base_url=base_url,
            query_params=query_params,
            **data
        )


@router.get("/{job_id}", response_model=JobOut)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    return await JobCrud(
        Job, JobCreate, JobUpdate, JobCrud.verbose_name
    ).read_single(
        db, id=job_id
    )


@router.put("/{job_id}", response_model=JobOut)
async def update_job(
    job_id: int, data: JobUpdate, db: AsyncSession = Depends(get_db)
):
    data: dict = data.dict(exclude_unset=True, exclude_defaults=True)
    return await JobCrud(
        Job, JobCreate, JobUpdate, JobCrud.verbose_name
    ).update(db, id=job_id, data=dict(data))

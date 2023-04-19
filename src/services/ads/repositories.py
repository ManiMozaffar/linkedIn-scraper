from typing import Optional

from fastapi import (
    Depends,
    APIRouter,
    Request,
    BackgroundTasks,
)
from sqlalchemy.ext.asyncio import AsyncSession
import redis


from services.common import PaginationQuery
from .models import Ads
from db import get_db, get_redis_db
from .schemas import AdsCreate, AdsUpdate, AdsOut, AdsQuery
from .factory import AdsCrud


router = APIRouter()


@router.post("", response_model=AdsOut)
async def create_ads(
    data: AdsCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    redis_db: redis.Redis = Depends(get_redis_db),
):
    data: dict = data.dict()
    result = await AdsCrud(
        Ads, AdsCreate, AdsUpdate, AdsCrud.verbose_name
    ).create(
        db_session=db, data=data, redis_db=redis_db,
        background_tasks=background_tasks
    )
    return result



@router.get("", response_model=None)
async def get_all_ads(
        request: Request,
        data: AdsQuery = Depends(),
        db: AsyncSession = Depends(get_db),
        paginated_data: PaginationQuery = Depends(),
        Ads_by: Optional[str] = None
):
    paginated_data: dict = paginated_data.dict(exclude_unset=True)
    query_params: dict = data.dict(exclude_unset=True, exclude_defaults=True)
    data: dict = query_params.copy()
    query_params.update(paginated_data)
    base_url = str(request.url_for(request.scope["endpoint"].__name__)).rstrip(
        "/"
    )
    return await AdsCrud(
            Ads, AdsCreate, AdsUpdate, AdsCrud.verbose_name
        ).paginated_read_all(
            db,
            Ads_by=Ads_by,
            base_url=base_url,
            query_params=query_params,
            **data
        )


@router.get("/{ads_id}", response_model=AdsOut)
async def get_ads(ads_id: str, db: AsyncSession = Depends(get_db)):
    return await AdsCrud(
        Ads, AdsCreate, AdsUpdate, AdsCrud.verbose_name
    ).read_single(
        db, ads_id=ads_id
    )


@router.put("/{ads_id}", response_model=AdsOut)
async def update_ads(
    ads_id: str, data: AdsUpdate, db: AsyncSession = Depends(get_db)
):
    data: dict = data.dict(exclude_unset=True, exclude_defaults=True)
    return await AdsCrud(
        Ads, AdsCreate, AdsUpdate, AdsCrud.verbose_name
    ).update(db, ads_id=ads_id, data=dict(data))

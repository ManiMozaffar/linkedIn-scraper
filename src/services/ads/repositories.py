from services.common import CRUD, PaginationQuery
from .models import Ads
from fastapi import Depends, APIRouter, Request
from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import AdsCreate, AdsUpdate, AdsOut, AdsQuery
from typing import Optional
from .utils import send_message_to_telegram

class AdsCrud(CRUD):
    verbose_name = "Advertisement"


router = APIRouter()


@router.post("", response_model=AdsOut)
async def create_Ads(data: AdsCreate, db: AsyncSession = Depends(get_db)):
    data: dict = data.dict()
    send_message_to_telegram(data)
    return await AdsCrud(
        Ads, AdsCreate, AdsUpdate, AdsCrud.verbose_name
    ).create(db, data=data)


@router.get("", response_model=None)
async def get_Adss(
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
    base_url = str(request.url_for(request.scope["endpoint"].__name__)).rstrip("/")
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
async def get_Ads(ads_id: int, db: AsyncSession = Depends(get_db)):
    return await AdsCrud(
        Ads, AdsCreate, AdsUpdate, AdsCrud.verbose_name
    ).read_single(
        db, id=ads_id
    )


@router.put("/{ads_id}", response_model=AdsOut)
async def update_Ads(
    ads_id: int, data: AdsUpdate, db: AsyncSession = Depends(get_db)
):
    data: dict = data.dict(exclude_unset=True, exclude_defaults=True)
    return await AdsCrud(
        Ads, AdsCreate, AdsUpdate, AdsCrud.verbose_name
    ).update(db, id=ads_id, data=dict(data))

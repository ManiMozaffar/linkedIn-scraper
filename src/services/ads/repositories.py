from services.common import CRUD, PaginationQuery
from .models import Ads
from fastapi import Depends, APIRouter, Request
from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import AdsCreate, AdsUpdate, AdsOut, AdsQuery
from typing import Optional
from .utils import send_message_to_telegram
from db import get_app_settings
from fastapi import HTTPException, status


class AdsCrud(CRUD):
    verbose_name = "Advertisement"

    async def create(self, db_session: AsyncSession, data: dict):
        if await self.model.objects.get(
            db_session=db_session, ads_id=data.get('ads_id')
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not Accepted, ads_id already exists"
            )
    
        text = f"""
**{data.get("title")}**
#{data.get("country")} #Linkedin


Location: {data.get("location")}
Company: {data.get("company_name")}


{data.get("body", "")}
        """
        result = await super().create(db_session, data)
        if result.id:
            send_message_to_telegram(
                chat_id=get_app_settings().telegram_chat_id,
                message_text=text,
                button_text="Apply",
                button_url=f"https://www.linkedin.com/jobs/view/{data.get('ads_id')}/"
            )
        return result


router = APIRouter()


@router.post("", response_model=AdsOut)
async def create_ads(data: AdsCreate, db: AsyncSession = Depends(get_db)):
    data: dict = data.dict()
    result = await AdsCrud(
        Ads, AdsCreate, AdsUpdate, AdsCrud.verbose_name
    ).create(db, data=data)
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

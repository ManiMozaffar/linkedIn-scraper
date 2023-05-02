from typing import Optional


from fastapi import Depends, APIRouter, Request
from sqlalchemy.ext.asyncio import AsyncSession


from services.common import PaginationQuery
from .models import Proxy
from db import get_db
from .schemas import ProxyCreate, ProxyUpdate, ProxyOut, ProxyQuery
from .factory import ProxyCrud

router = APIRouter()


@router.post("", response_model=ProxyOut)
async def create_Proxy(data: ProxyCreate, db: AsyncSession = Depends(get_db)):
    data: dict = data.dict()
    return await ProxyCrud(
        Proxy, ProxyCreate, ProxyUpdate, ProxyCrud.verbose_name
    ).create(db, data=data)


@router.get("", response_model=None)
async def get_Proxys(
        request: Request,
        data: ProxyQuery = Depends(),
        db: AsyncSession = Depends(get_db),
        paginated_data: PaginationQuery = Depends(),
        order_by: Optional[str] = None
):
    paginated_data: dict = paginated_data.dict(exclude_unset=True)
    query_params: dict = data.dict(exclude_unset=True, exclude_defaults=True)
    data: dict = query_params.copy()
    query_params.update(paginated_data)
    base_url = str(request.url_for(
        request.scope["endpoint"].__name__)
    ).rstrip("/")
    return await ProxyCrud(
            Proxy, ProxyCreate, ProxyUpdate, ProxyCrud.verbose_name
        ).paginated_read_all(
            db,
            order_by=order_by,
            base_url=base_url,
            query_params=query_params,
            **data
        )


@router.get("/{proxy_id}", response_model=ProxyOut)
async def get_Proxy(proxy_id: int, db: AsyncSession = Depends(get_db)):
    return await ProxyCrud(
        Proxy, ProxyCreate, ProxyUpdate, ProxyCrud.verbose_name
    ).read_single(
        db, id=proxy_id
    )


@router.put("/{proxy_id}", response_model=ProxyOut)
async def update_Proxy(
    proxy_id: int, data: ProxyUpdate, db: AsyncSession = Depends(get_db)
):
    data: dict = data.dict(exclude_unset=True, exclude_defaults=True)
    return await ProxyCrud(
        Proxy, ProxyCreate, ProxyUpdate, ProxyCrud.verbose_name
    ).update(db, id=proxy_id, data=dict(data))

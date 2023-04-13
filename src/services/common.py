from pydantic import BaseModel, HttpUrl, Field
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from orm.models import AbstractModel
from db import get_db
from typing import Union, Optional, Tuple, List
from urllib.parse import urlencode
from datetime import datetime
from sqlalchemy import Column, DateTime


class AbstractModeDateMixin(AbstractModel):
    __abstract__ = True
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Status(BaseModel):
    message: str


class PaginationQuery(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(10, le=50)


class PaginatedObjects(BaseModel):
    results: List[AbstractModel]
    page: Union[None, int]
    count: Union[None, int]
    next_page: Union[None, HttpUrl]
    previous_page: Union[None, HttpUrl]

    class Config:
        arbitrary_types_allowed = True


class BaseCRUD:
    verbose_name: str
    order_by_fields: Union[None, Tuple, str]

    def __init__(
            self, model: AbstractModel,
            in_schema: BaseModel,
            update_schema: BaseModel,
            name: str
    ):
        self.model = model
        self.in_schema = in_schema
        self.update_schema = update_schema
        self.verbose_name = name

    @property
    def _order_by_fields(self):
        cached_order_by_fields = getattr(self, "order_by_fields", None)
        if cached_order_by_fields in ["__all__", ("__all__")]:
            return self.model.__table__.columns.keys()
        else:
            return cached_order_by_fields

    @_order_by_fields.setter
    def _order_by_fields(self, value):
        if (
            isinstance(value, str) or isinstance(value, tuple)
        ) and self.init_order_by(value):
            self._order_by_fields = value
        else:
            raise ValueError("order_by_fields is not a valid string/tuple")

    def init_order_by(self, order_by):
        fields = [field.strip("-") for field in order_by.split(",")]
        invalid_fields = set(fields) - set(self.model.__table__.columns.keys())
        if invalid_fields:
            raise ValueError("order_by contains invalid fields: {}".format(", ".join(invalid_fields)))
        return True

    def is_order_by_valid(self, order_by):
        fields = [field.strip("-") for field in order_by.split(",")]
        return all(field in self._order_by_fields for field in fields)


class ConstructorMixin:
    async def pre_save_check(self, db_session: AsyncSession, data: dict):
        pass

    async def pre_update_check(self, db_session: AsyncSession, data: dict):
        pass

    async def pre_delete_check(self, db_session: AsyncSession):
        pass


class CRUD(BaseCRUD, ConstructorMixin):

    async def create(self, db_session: AsyncSession, data: dict):
        await self.pre_save_check(db_session, data)
        instance = await self.model.objects.create(db_session=db_session, **data)
        return instance

    async def delete(self, db_session: AsyncSession, joins=set(), **kwargs):
        await self.pre_delete_check(db_session)
        deleted_rows = await self.model.objects.delete(
            db_session=db_session, joins=joins, **kwargs
        )
        return deleted_rows

    async def read_all(
            self,  db_session: AsyncSession = Depends(get_db()),
            joins=set(),
            order_by: Optional[str] = None,
            skip: int = None,
            per_page: int = None,
            **kwargs
    ):
        if order_by and order_by != "?":
            if not self.is_order_by_valid(order_by):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{self.verbose_name} with the specified field for order_by is not found, please use one of these fields: {self._order_by_fields}"
                )
            else:
                order_by = tuple(order_by.split(","))

        result = await self.model.objects.filter(
            joins=joins,
            order_by=order_by,
            skip=skip,
            limit=per_page,
            **kwargs
        ).execute(db_session=db_session)
        return result

    async def paginated_read_all(
            self,
            db_session: AsyncSession = Depends(get_db()),
            joins=set(), order_by: Optional[str] = None, 
            base_url=None, query_params: dict() = dict(),
            **kwargs
    ):
        per_page = query_params.get('per_page')
        page_num = query_params.get('page')

        if order_by:
            query_params.update(order_by=order_by)

        skip = (page_num - 1) * per_page
        results = await self.read_all(
            db_session, order_by=order_by, skip=skip, per_page=per_page,
            joins=joins, get_count=True, **kwargs
        )
        count = 30
        next_page = None
        previous_page = None

        if (page_num * per_page) < count:
            next_query_params = urlencode(
                {**query_params, "page": page_num + 1}
            )
            next_page = f"{base_url}?{next_query_params}"

        if (page_num - 1) > 0 and  0 < ((page_num-1) * per_page) < count+per_page:
            prev_query_params = urlencode(
                {**query_params, "page": page_num - 1}
            )
            previous_page = f"{base_url}?{prev_query_params}"

        return dict(
            results=results, page=page_num, count=count,
            previous_page=previous_page, next_page=next_page
        )

    async def read_single(
            self, db_session: AsyncSession = Depends(get_db()), joins=set(), **kwargs
    ):
        result = await self.model.objects.get(
            db_session=db_session, joins=joins, **kwargs
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.verbose_name} with the specified filters is not found"
            )
        return result

    async def update(
            self, db_session: AsyncSession, data: dict, joins=set(), **kwargs
    ):
        await self.pre_update_check(db_session, data)
        updated_instance = await self.model.objects.update(
            db_session=db_session, data=data, joins=set(), **kwargs
        )
        if updated_instance is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"{self.verbose_name} with the specified filters is not found")
        return updated_instance

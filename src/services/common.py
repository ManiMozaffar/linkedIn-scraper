import logging
from typing import Union, Optional, Tuple, List, Set, Callable
from urllib.parse import urlencode
from datetime import datetime

import time
import redis
from pydantic import BaseModel, HttpUrl, Field
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, DateTime


from orm.models import AbstractModel
from db import get_db
from . import utils


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
            raise ValueError(
                "order_by contains invalid fields: {}".format(
                    ", ".join(invalid_fields)
                ))
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
        instance = await self.model.objects.create(
            db_session=db_session, **data
        )
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
            get_count: bool = False,
            **kwargs
    ):
        if order_by and order_by != "?":
            if not self.is_order_by_valid(order_by):
                text = f"{self.verbose_name} with the specified field for"
                text += "order_by is not found, please use one of"
                text += f"these fields : {self._order_by_fields}"
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=text
                )
            else:
                order_by = tuple(order_by.split(","))
        query = self.model.objects.filter(
            joins=joins,
            order_by=order_by,
            skip=skip,
            limit=per_page,
            **kwargs
        )
        count = await query.count(db_session) if get_count else None
        result = await query.execute(db_session=db_session)

        if get_count:
            return result, count
        else:
            return query

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
        results, count = await self.read_all(
            db_session, order_by=order_by, skip=skip, per_page=per_page,
            joins=joins, get_count=True, **kwargs
        )
        next_page = None
        previous_page = None

        if (page_num * per_page) < count:
            next_query_params = urlencode(
                {**query_params, "page": page_num + 1}
            )
            next_page = f"{base_url}?{next_query_params}"

        if (page_num - 1) > 0 and 0 < (
            (page_num-1) * per_page
        ) < count+per_page:
            prev_query_params = urlencode(
                {**query_params, "page": page_num - 1}
            )
            previous_page = f"{base_url}?{prev_query_params}"

        return dict(
            results=results, page=page_num, count=count,
            previous_page=previous_page, next_page=next_page
        )

    async def read_single(
        self,
        db_session: AsyncSession = Depends(get_db()),
        joins=set(),
        **kwargs
    ):
        result = await self.model.objects.get(
            db_session=db_session, joins=joins, **kwargs
        )
        if not result:
            text = f"{self.verbose_name} with specified filter is not found"
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=text
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
            text = f"{self.verbose_name} with specified filter is not found"
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=text
            )
        return updated_instance


class RedisCrud:
    def __init__(self, db: redis.Redis):
        self.db = db

    def filter_by_keywords(self, keywords: List[str]) -> Set:
        return self.find_unoin_values(
            self.get_by_keyword(keyword) for keyword in keywords
        )

    def find_unoin_values(self, sets: List[Set]) -> Set:
        return set.union(*sets)

    def get_by_keyword(self, keyword: str) -> Set:
        value = self.db.get(keyword)
        return utils.to_set(value) if value else set()

    def get_by_keywords(self, keywords: str) -> Set:
        return set.union(
            *(self.get_by_keyword(keyword) for keyword in keywords)
        )

    def _update_set_with_function(
        self,
        keyword: str,
        update_function: Callable,
        max_retries: int = 3,
        retry_interval: int = 1,
        **kwargs
    ) -> Set:
        pipeline = self.db.pipeline()
        retries = 0
        while retries < max_retries:
            try:
                pipeline.watch(keyword)
                current_value = utils.to_set(self.db.get(keyword) or set())
                update_function(current_value)
                pipeline.multi()
                pipeline.set(keyword, utils.to_str(current_value), **kwargs)
                pipeline.execute()
                break
            except redis.WatchError:
                retries += 1
                time.sleep(retry_interval)
            finally:
                pipeline.reset()

        if retries == max_retries:
            logging.error(
                f"Failed to update '{keyword}' after {max_retries} retries."
            )

        return list(utils.to_set(self.db.get(keyword)))

    def reset(
        self,
        keyword: str,
        max_retries: int = 3,
        retry_interval: int = 1
    ) -> Set:
        return self._update_set_with_function(
            keyword,
            lambda current_value: current_value.clear(),
            max_retries,
            retry_interval
        )

    def add(
        self,
        keyword: str,
        new_data,
        max_retries: int = 3,
        retry_interval: int = 1,
        **kwargs
    ) -> Set:
        return self._update_set_with_function(
            keyword,
            lambda current_val: current_val.update(new_data),
            max_retries,
            retry_interval,
            **kwargs
        )

    def delete(
        self,
        keyword: str,
        deleted_data,
        max_retries: int = 3,
        retry_interval: int = 1
    ) -> Set:
        return self._update_set_with_function(
            keyword,
            lambda current_val: current_val.difference_update(deleted_data),
            max_retries,
            retry_interval
        )

    def reset_and_add(
        self,
        keyword: str,
        new_data,
        max_retries: int = 3,
        retry_interval: int = 1
    ) -> list:
        self.reset(keyword, max_retries, retry_interval)
        return self.add(keyword, new_data, max_retries, retry_interval)

    def get(self, keywords: list) -> Set:
        return self.get_by_keywords(keywords)

    def all(self, keywords: list) -> Set:
        return list(self.filter_by_keywords(keywords))

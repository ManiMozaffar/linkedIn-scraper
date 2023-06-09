from fastapi import APIRouter, Depends
import redis


from .schemas import (
    RelatedUserTechFilter,
    RelatedUserTechCreate,
    KeywordIn,
    ResultListOut,
    RelatedUserTechDelete
)
from db import get_redis_db
from .factory import KeyWordCrud


router = APIRouter()


@router.post("/keywords", response_model=ResultListOut)
async def create_keyword(
    data: KeywordIn, db: redis.Redis = Depends(get_redis_db())
):
    keyword = data.dict().get("keywords")
    return dict(
        result=KeyWordCrud(db).create_keyword(keyword)
    )


@router.get("/keywords", response_model=ResultListOut)
async def all_keywords(
    db: redis.Redis = Depends(get_redis_db())
):
    return dict(
        result=KeyWordCrud(db).get_all_keywords()
    )


@router.delete("/keywords", response_model=ResultListOut)
async def delete_keywords(
    data: KeywordIn, db: redis.Redis = Depends(get_redis_db())
):
    keyword = data.dict().get("keywords")
    return dict(
        result=KeyWordCrud(db).delete_keywords(keyword)
    )


@router.post("", response_model=ResultListOut)
async def create_related_user_tech(
    data: RelatedUserTechCreate, db: redis.Redis = Depends(get_redis_db())
):
    data: dict = data.dict()
    return dict(
        result=KeyWordCrud(db).append_related_user_tech(
            data.get("keyword"), data.get("value")
        )
    )


@router.post("/query", response_model=ResultListOut)
async def filter_related_user_tech(
    data: RelatedUserTechFilter, db: redis.Redis = Depends(get_redis_db())
):
    keywords = data.dict().get("keywords")
    return dict(
        result=KeyWordCrud(db).union_related_user_tech(keywords)
    )


@router.get("/{tech}", response_model=ResultListOut)
async def get_related_user_tech(
    tech: str, db: redis.Redis = Depends(get_redis_db())
):
    return dict(
        result=KeyWordCrud(db).get_related_user_tech(tech)
    )


@router.delete("", response_model=ResultListOut)
async def delete_related_user_tech(
    data: RelatedUserTechDelete, db: redis.Redis = Depends(get_redis_db())
):
    data: dict = data.dict()
    return dict(
        result=KeyWordCrud(db).delete_related_user_tech(
            data.get("keyword"), data.get("value")
        )
    )

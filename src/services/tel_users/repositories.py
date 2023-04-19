from fastapi import APIRouter, Depends, Response, status
import redis
from .schemas import (
    UserOut,
    UserIn,
    UserFilter,
    ForwardMessage
)
from db import get_redis_db
from .factory import TelegramCrud, TelegramRetriever

router = APIRouter()


@router.post("/user/{user_id}")
async def check_user_expression(
    user_id: str, data: UserFilter,
    db: redis.Redis = Depends(get_redis_db())
):
    crud_obj = TelegramCrud(db)
    resp = TelegramCrud(db).eval(
        user_expression=crud_obj.get_user_expression(user_id),
        context=crud_obj.get_context,
        ads_keywords=data.dict()["filters"]
    )
    return resp


@router.put("/user/{user_id}")
async def update_expression(
    user_id: str, data: UserIn,
    db: redis.Redis = Depends(get_redis_db())
):
    crud_obj = TelegramCrud(db)
    resp = TelegramCrud(db).update_user_expression(
        user_id=user_id,
        user_expression=data.dict()["expression"],
        context=crud_obj.get_context,
        ads_keywords="python or django"
    )
    return resp


@router.get("/user/{user_id}")
async def get_user_expression(
    user_id: str,
    db: redis.Redis = Depends(get_redis_db())
):
    return dict(result=TelegramCrud(db).get([user_id]))


@router.delete("/{user_id}", response_model=UserOut)
async def delete_user(
    user_id: str, db: redis.Redis = Depends(get_redis_db())
):
    TelegramCrud(db).reset(user_id)
    return Response(status_code=status.HTTP_200_OK)


@router.get("/users")
async def get_all_users(
    db: redis.Redis = Depends(get_redis_db())
):
    return dict(
        users=TelegramRetriever(db).get_all_active_users()
    )


@router.get("/filters")
async def get_all_filters(
    db: redis.Redis = Depends(get_redis_db())
):
    return dict(
        users=TelegramRetriever(db).get_all_filters()
    )

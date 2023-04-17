from fastapi import APIRouter, Depends, Response, status
import redis
from .schemas import (
    UserOut,
    UserIn,
    UserFilter
)
from services.common import RedisCrud
from db import get_redis_db
import requests
import re


class TelegramCrud(RedisCrud):
    @property
    def get_context(self):
        return list(self.get(["keywords"]))

    def get_user_expression(self, user_id: int):
        result = self.get([user_id])
        return None if len(result) == 0 else result.pop()

    def eval(self, context, user_expression, ads_keywords) -> dict:
        payload = {
            "context": context,
            "expression": user_expression,
            "filter": ads_keywords
        }
        resp = requests.Session().post("http://isolated:9999", json=payload)
        return resp.json()

    def update_user_expression(
            self, user_id, context, user_expression, ads_keywords,
            regex=r'\b(?!\band\b|\bor\b)\w+\b'
    ):
        old_expression = self.get_user_expression(user_id)
        if old_expression:
            for namespace in set(re.findall(regex, old_expression)):
                print(namespace, [user_id])
                self.delete(namespace, [user_id])

        resp = self.eval(
            context, user_expression, ads_keywords
        )
        if resp.get("success"):
            self.reset_and_add(user_id, [user_expression])
            for namespace in resp.get("namespaces"):
                self.add(namespace, [user_id, ])
        return resp


router = APIRouter()


@router.post("/{user_id}")
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


@router.put("/{user_id}")
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


@router.get("/{user_id}")
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

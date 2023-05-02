import logging

from sqlalchemy.ext.asyncio import AsyncSession
import redis
from fastapi import HTTPException, status, BackgroundTasks


from services.common import CRUD
from . import tasks
from db import get_app_settings
from .utils import send_message_to_telegram


class AdsCrud(CRUD):
    verbose_name = "Advertisement"

    async def create(
            self,
            db_session: AsyncSession,
            data: dict,
            background_tasks: BackgroundTasks,
            redis_db: redis.Redis
    ):
        if await self.model.objects.get(
            db_session=db_session, ads_id=data.get('ads_id')
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not Accepted, ads_id already exists"
            )

        text = f"""
{data.get("title")}
#{data.get("country")} #Linkedin


Location: {data.get("location")}
Company: {data.get("company_name")}


{data.get("body", "")}
        """
        sql_creation_data = data.copy()
        sql_creation_data.pop("tags", None)
        sql_creation_data.pop("keywords", None)
        result = await super().create(db_session, sql_creation_data)
        if result.id:
            ads_id = data.get('ads_id')
            message: dict = send_message_to_telegram(
                chat_id=get_app_settings().telegram_chat_id,
                message_text=text,
                button_text="Apply",
                button_url=f"https://www.linkedin.com/jobs/view/{ads_id}/"
            )
            keywords = data.get("keywords")
            if keywords and len(keywords) > 0 and message:
                background_tasks.add_task(
                    tasks.send_message_to_filtered_users,
                    redis_db,
                    message.get("message_id"),
                    message.get("chat").get("id"),
                    keywords
                )
            else:
                logging.error("Task not started; keywords={keywords}")
        return result

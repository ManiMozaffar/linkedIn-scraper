from pydantic import BaseModel
from typing import Optional
import datetime


class AdsOut(BaseModel):
    id: int
    ads_id: int
    location: str
    body: str
    company_name: str
    source: int
    published_at: datetime.datetime
    employement_type: str
    level: str

    class Config:
        orm_mode = True


class AdsUpdate(BaseModel):
    ads_id: int
    location: str
    body: str
    company_name: str
    source: int
    published_at: datetime.datetime
    employement_type: str
    level: str


class AdsQuery(BaseModel):
    ads_id: int
    location: str
    company_name: str
    source: int
    employement_type: str
    level: str


class AdsCreate(AdsUpdate):
    pass

from pydantic import BaseModel
from typing import Optional
import datetime


class AdsOut(BaseModel):
    id: int
    ads_id: str
    location: str
    title: str
    body: str
    company_name: str
    source: int
    employement_type: str
    level: str

    class Config:
        orm_mode = True


class AdsUpdate(BaseModel):
    ads_id: str
    location: str
    body: str
    company_name: str
    title: str
    source: int
    employement_type: str
    level: str


class AdsQuery(BaseModel):
    ads_id: Optional[int]
    location: Optional[str]
    company_name: Optional[str]
    source: Optional[int]
    title: Optional[str]
    employement_type: Optional[str]
    level: Optional[str]


class AdsCreate(AdsUpdate):
    pass

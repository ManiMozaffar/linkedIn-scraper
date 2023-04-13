from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from db import Base
from services.common import AbstractModeDateMixin


class Ads(Base, AbstractModeDateMixin):
    __tablename__ = 'advertisments'
    id = Column(Integer, primary_key=True, index=True)
    ads_id = Column(Integer, primary_key=True, index=True)
    location = Column(String(50))
    country = Column(String(50))
    body = Column(String(5_000))
    company_name = Column(String(300))
    source = Column(Integer)
    published_at = Column(DateTime, default=datetime.utcnow)
    employement_type = Column(String(100))
    level = Column(String(100))

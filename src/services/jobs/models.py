from sqlalchemy import Column, Integer, String

from db import Base
from services.common import AbstractModeDateMixin


class Job(Base, AbstractModeDateMixin):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)

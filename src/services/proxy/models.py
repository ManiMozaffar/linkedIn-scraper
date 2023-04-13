from sqlalchemy import Column, Integer, String

from db import Base
from services.common import AbstractModeDateMixin


class Proxy(Base, AbstractModeDateMixin):
    __tablename__ = 'proxies'
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(50))
    port = Column(Integer)
    username = Column(String(50))
    password = Column(String(50))

from pydantic import BaseModel
from typing import Optional


class ProxyOut(BaseModel):
    id: int
    ip_address: str
    port: int
    username: Optional[str]
    password: Optional[str]

    class Config:
        orm_mode = True


class ProxyUpdate(BaseModel):
    ip_address: str
    port: int
    username: Optional[str]
    password: Optional[str]


class ProxyQuery(BaseModel):
    ip_address: Optional[str]
    port: Optional[int]


class ProxyCreate(ProxyUpdate):
    pass

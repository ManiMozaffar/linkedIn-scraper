from pydantic import BaseModel
from typing import Optional
from pydantic import Field
from services.common import PaginationQuery


class CustomPaginationQuery(PaginationQuery):
    page: int = Field(1, ge=1)
    per_page: int = Field(1000, le=1000)


class JobOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class JobUpdate(BaseModel):
    name: str


class JobQuery(BaseModel):
    name: Optional[str]


class JobCreate(JobUpdate):
    pass

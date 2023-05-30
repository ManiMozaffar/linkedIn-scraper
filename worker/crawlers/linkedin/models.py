from typing import Optional

from pydantic import BaseModel, AnyUrl

from crawlers.linkedin.enums import JobModels


class LinkedinURLData(BaseModel):
    url: AnyUrl
    country: str
    job_mode: JobModels
    ads_id: Optional[str]


class LinkedinData(BaseModel):
    ads_id: str
    location: Optional[str]
    country: str
    body: str
    company_name: Optional[str]
    title: str
    source: int = 1
    employement_type: Optional[JobModels]
    level: Optional[str]
    keywords: list = list()

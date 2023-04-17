from pydantic import BaseModel


class ResultListOut(BaseModel):
    result: list

    class Config:
        orm_mode = True


class RelatedUserTechDelete(BaseModel):
    keyword: str
    value: list


class RelatedUserTechCreate(RelatedUserTechDelete):
    pass


class RelatedUserTechFilter(BaseModel):
    keywords: list


class KeywordIn(BaseModel):
    keywords: list

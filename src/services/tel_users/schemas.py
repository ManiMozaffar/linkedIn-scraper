from pydantic import BaseModel


class UserOut(BaseModel):
    result: bool

    class Config:
        orm_mode = True


class UserIn(BaseModel):
    expression: str


class UserFilter(BaseModel):
    filters: list


class ForwardMessage(BaseModel):
    message_id: str
    from_chat_id: str

from datetime import datetime
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class FaqBase(BoilerplateBaseModel):
    question: str
    answer: str
    category: str


class FaqCreate(FaqBase):
    pass


class FaqUpdate(FaqBase):
    pass


class FaqCreated(FaqBase):
    id: UUID
    created_at: datetime
    modified_at: datetime


class FaqInDBBase(FaqBase):
    id: UUID
    created_at: datetime
    modified_at: datetime

    class Config:
        from_attributes = True


class FaqSchema(FaqInDBBase):
    pass

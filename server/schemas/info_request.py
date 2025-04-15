from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class InfoRequestBase(BoilerplateBaseModel):
    email: str
    product_id: UUID
    shop_id: UUID


class InfoRequestCreate(InfoRequestBase):
    pass

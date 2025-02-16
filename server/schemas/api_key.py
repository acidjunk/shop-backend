from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


# Properties to receive via API on creation
class APIKeyCreate(BaseModel):
    shop_id: UUID
    hashed_key: str


# Additional properties stored in DB
class APIKeyInDBBase(BaseModel):
    id: UUID
    shop_id: UUID
    created_at: datetime
    revoked_at: Optional[datetime]


class APIKeyInDBGet(APIKeyInDBBase):
    pass


# During creation of an API key, we return the raw key a single time
class APIKeyInDBCreate(APIKeyInDBBase):
    api_key: str

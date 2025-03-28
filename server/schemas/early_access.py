from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class EarlyAccessBase(BaseModel):
    email: EmailStr
    # maybe might still be needed
    # member_first_name: Optional[str] = None
    # member_infix: Optional[str] = None
    # member_last_name: Optional[str] = None


# Properties to receive via API on creation
class EarlyAccessCreate(EarlyAccessBase):
    pass


class EarlyAccessInDBBase(EarlyAccessBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Additional properties to return via API
# class EarlyAccess(EarlyAccessInDBBase):
#     created_at = datetime

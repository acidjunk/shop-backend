# Copyright 2024 René Dohmen <acidjunk@gmail.com>
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    username: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: UUID
    created_at: datetime
    # updated_at: datetime

    class Config:
        from_attributes = True


# Additional properties to return via API
class User(UserInDBBase):
    created_at: datetime
    # updated_at: datetime


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str


class UserShops(BaseModel):
    shops: List[UUID]

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
"""Schemas for the cross-shop admin accounts endpoints.

These intentionally live next to but separate from
:mod:`server.schemas.account` — the latter is the lightweight shape
returned by the shop-scoped CRUD endpoints, while these expose extra
derived fields (``shop_name``, surfaced ``stripe_customer_id`` /
``stripe_synced_at``) that an admin investigator needs without
having to inspect the raw ``details`` JSON column.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from server.db.models import Account
from server.schemas.base import BoilerplateBaseModel


class AdminAccountSchema(BoilerplateBaseModel):
    id: UUID
    shop_id: Optional[UUID] = None
    shop_name: Optional[str] = None
    name: Optional[str] = None
    hash_name: Optional[str] = None
    details: Optional[dict] = None
    stripe_customer_id: Optional[str] = None
    stripe_synced_at: Optional[datetime] = None


class LinkStripeBody(BoilerplateBaseModel):
    stripe_customer_id: str


class SyncStripeResponse(BoilerplateBaseModel):
    id: UUID
    stripe_customer_id: str
    stripe_synced_at: datetime
    stripe_customer: dict


def build_admin_account(account: Account) -> AdminAccountSchema:
    """Project an :class:`Account` ORM row into :class:`AdminAccountSchema`.

    Reads ``details`` defensively (it may be ``None`` or missing keys)
    and surfaces the Stripe convenience fields at the top level. Pulls
    ``shop_name`` via the relationship — caller should ``joinedload``
    it for list endpoints to avoid N+1.
    """
    details = account.details if isinstance(account.details, dict) else {}
    synced_at_raw = details.get("stripe_synced_at") if details else None
    synced_at: Optional[datetime] = None
    if isinstance(synced_at_raw, str):
        try:
            synced_at = datetime.fromisoformat(synced_at_raw)
        except ValueError:
            synced_at = None
    elif isinstance(synced_at_raw, datetime):
        synced_at = synced_at_raw

    return AdminAccountSchema(
        id=account.id,
        shop_id=account.shop_id,
        shop_name=account.shop.name if account.shop is not None else None,
        name=account.name,
        hash_name=account.hash_name,
        details=details or None,
        stripe_customer_id=details.get("stripe_customer_id") if details else None,
        stripe_synced_at=synced_at,
    )

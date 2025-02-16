from uuid import UUID

import structlog

from server.db import db
from server.db.models import APIKeyTable
from server.security import generate_api_key

logger = structlog.getLogger(__name__)


def make_api_key(shop_id: UUID):
    _key, hashed_key = generate_api_key()
    api_key = APIKeyTable(shop_id=shop_id, hashed_key=hashed_key)
    db.session.add(api_key)
    db.session.commit()
    return api_key.id

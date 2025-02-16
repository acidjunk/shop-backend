from uuid import UUID

import structlog

from server.db import db
from server.db.models import APIKeyTable
from server.security import generate_api_key

logger = structlog.getLogger(__name__)


def make_api_key(user_id: UUID):
    key, fingerprint, encrypted_key = generate_api_key()
    api_key = APIKeyTable(user_id=user_id, fingerprint=fingerprint, encrypted_key=encrypted_key)
    db.session.add(api_key)
    db.session.commit()
    return api_key.id, key

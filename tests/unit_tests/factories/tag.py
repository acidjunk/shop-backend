from uuid import UUID

import structlog

from server.db import db
from server.db.models import TagTable, TagTranslationTable

logger = structlog.getLogger(__name__)


def make_tag(shop_id: UUID, main_name="Tag for Testing", alt1_name="Tag voor Testen", alt2_name="Tag zum Testen"):
    tag = TagTable(shop_id=shop_id, name=main_name)
    db.session.add(tag)
    db.session.commit()

    # translation
    trans = TagTranslationTable(tag_id=tag.id, main_name=main_name, alt1_name=alt1_name, alt2_name=alt2_name)
    db.session.add(trans)
    db.session.commit()
    return tag.id

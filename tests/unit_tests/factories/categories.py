from uuid import UUID

import structlog

from server.db import db
from server.db.models import CategoryTable, CategoryTranslationTable

logger = structlog.getLogger(__name__)


def make_category(shop_id: UUID, main_name="Main name", main_description="Main description"):
    category = CategoryTable(shop_id=shop_id)
    db.session.add(category)
    db.session.commit()

    # create translations
    trans = CategoryTranslationTable(category_id=category.id, main_name=main_name, main_description=main_description)
    db.session.add(trans)
    db.session.commit()

    return category.id


def make_category_translated(
    shop_id: UUID,
    main_name="Main name",
    alt1_name="Alt1 name",
    alt2_name="Alt2 name",
):
    category = CategoryTable(shop_id=shop_id)
    db.session.add(category)
    db.session.commit()

    # create translations
    trans = CategoryTranslationTable(
        category_id=category.id, main_name=main_name, alt1_name=alt1_name, alt2_name=alt2_name
    )
    db.session.add(trans)
    db.session.commit()

    return category.id

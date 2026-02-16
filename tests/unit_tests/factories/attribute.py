from server.db import db
from server.db.models import AttributeTable, AttributeOptionTable, ProductAttributeValueTable


def make_attribute(shop_id, name="size", unit=None):
    attr = AttributeTable(shop_id=shop_id, name=name, unit=unit)
    db.session.add(attr)
    db.session.commit()
    return attr.id


def make_option(attribute_id, value_key: str):
    opt = AttributeOptionTable(attribute_id=attribute_id, value_key=value_key)
    db.session.add(opt)
    db.session.commit()
    return opt.id


def make_pav(product_id, attribute_id, option_id=None):
    pav = ProductAttributeValueTable(product_id=product_id, attribute_id=attribute_id, option_id=option_id)
    db.session.add(pav)
    db.session.commit()
    return pav.id
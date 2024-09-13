import structlog

from server.db import ShopTable, db

logger = structlog.getLogger(__name__)


def make_shop(
    with_config=False,
):
    if with_config:
        config = {
            "config": {
                "short_shop_name": "string",
                "main_banner": "string",
                "alt1_banner": "string",
                "alt2_banner": "string",
                "languages": {
                    "main": {
                        "language_name": "string",
                        "menu_items": {
                            "about": "string",
                            "cart": "string",
                            "checkout": "string",
                            "products": "string",
                            "contact": "string",
                            "policies": "string",
                            "terms": "string",
                            "privacy_policy": "string",
                            "return_policy": "string",
                            "website": "string",
                            "phone": "string",
                            "email": "string",
                            "address": "string",
                        },
                        "static_texts": {
                            "about": "string",
                            "terms": "string",
                            "privacy_policy": "string",
                            "return_policy": "string",
                        },
                    },
                    "alt1": {
                        "language_name": "string",
                        "menu_items": {
                            "about": "string",
                            "cart": "string",
                            "checkout": "string",
                            "products": "string",
                            "contact": "string",
                            "policies": "string",
                            "terms": "string",
                            "privacy_policy": "string",
                            "return_policy": "string",
                            "website": "string",
                            "phone": "string",
                            "email": "string",
                            "address": "string",
                        },
                        "static_texts": {
                            "about": "string",
                            "terms": "string",
                            "privacy_policy": "string",
                            "return_policy": "string",
                        },
                    },
                    "alt2": {
                        "language_name": "string",
                        "menu_items": {
                            "about": "string",
                            "cart": "string",
                            "checkout": "string",
                            "products": "string",
                            "contact": "string",
                            "policies": "string",
                            "terms": "string",
                            "privacy_policy": "string",
                            "return_policy": "string",
                            "website": "string",
                            "phone": "string",
                            "email": "string",
                            "address": "string",
                        },
                        "static_texts": {
                            "about": "string",
                            "terms": "string",
                            "privacy_policy": "string",
                            "return_policy": "string",
                        },
                    },
                },
                "contact": {
                    "company": "string",
                    "website": "https://example.com/",
                    "phone": "strings",
                    "email": "user@example.com",
                    "address": "string",
                    "twitter": "https://example.com/",
                    "facebook": "https://example.com/",
                    "instagram": "https://example.com/",
                },
            },
            "config_version": 0,
        }
        shop = ShopTable(name="Test Shop", description="Test Shop Description", config=config)
    else:
        shop = ShopTable(name="Test Shop", description="Test Shop Description")
    db.session.add(shop)
    db.session.commit()
    return shop.id

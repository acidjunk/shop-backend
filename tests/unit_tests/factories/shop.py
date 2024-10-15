import json

import structlog

from server.db import ShopTable, db
from server.schemas.shop import (
    ConfigurationContact,
    ConfigurationHomepageSections,
    ConfigurationLanguageFieldMenuItems,
    ConfigurationLanguageFields,
    ConfigurationLanguageFieldStaticTexts,
    ConfigurationLanguages,
    ConfigurationV1,
    ShopConfig,
    ShopConfigUpdate,
)

logger = structlog.getLogger(__name__)


def make_shop(
    with_config=False,
):
    if with_config:
        menu_items = ConfigurationLanguageFieldMenuItems(
            about="string",
            cart="string",
            checkout="string",
            products="string",
            contact="string",
            policies="string",
            terms="string",
            privacy_policy="string",
            return_policy="string",
            website="string",
            phone="string",
            email="string",
            address="string",
        )

        static_texts = ConfigurationLanguageFieldStaticTexts(
            about="string", terms="string", privacy_policy="string", return_policy="string"
        )

        language_fields = ConfigurationLanguageFields(
            language_name="string", menu_items=menu_items, static_texts=static_texts
        )

        homepage_sections = ConfigurationHomepageSections(
            show_new_products=True, show_featured_products=True, show_categories=True
        )

        config_languages = ConfigurationLanguages(main=language_fields, alt1=language_fields, alt2=language_fields)

        config_contact = ConfigurationContact(
            company="string",
            website="https://example.com/",
            phone="+31 6 12345678",
            email="user@example.com",
            address="string",
            twitter="https://example.com/",
            facebook="https://example.com/",
            instagram="https://example.com/",
        )

        top_config = ConfigurationV1(
            languages=config_languages,
            short_shop_name="string",
            main_banner="string",
            alt1_banner="string",
            alt2_banner="string",
            contact=config_contact,
            homepage_sections=homepage_sections,
        )

        config = ShopConfigUpdate(config=top_config, config_version=0)

        shop = ShopTable(
            name="Test Shop",
            description="Test Shop Description",
            config=config.model_dump(),
            stripe_public_key="string",
        )
    else:
        shop = ShopTable(name="Test Shop", description="Test Shop Description", stripe_public_key="string")
    db.session.add(shop)
    db.session.commit()
    return shop.id

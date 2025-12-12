import json

import structlog

from server.db import ShopTable, db
from server.schemas.shop import (
    ConfigurationContact,
    ConfigurationLanguageFieldMenuItems,
    ConfigurationLanguageFields,
    ConfigurationLanguageFieldStaticTexts,
    ConfigurationLanguages,
    ConfigurationV1,
    ShopConfig,
    ShopConfigUpdate,
    Toggles,
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

        toggles = Toggles(
            show_new_products=True,
            show_featured_products=True,
            show_categories=True,
            show_shop_name=True,
            show_nav_categories=False,
            language_alt1_enabled=False,
            language_alt2_enabled=False,
            enable_stock_on_products=True
        )

        config_languages = ConfigurationLanguages(main=language_fields, alt1=language_fields, alt2=language_fields)

        config_contact = ConfigurationContact(
            company="string",
            website="https://example.com/",
            phone="+31 6 12345678",
            email="user@example.com",
            address="string",
            zip_code="string",
            city="string",
            twitter="https://example.com/",
            facebook="https://example.com/",
            instagram="https://example.com/",
        )

        config = ConfigurationV1(
            languages=config_languages,
            short_shop_name="string",
            main_banner="string",
            alt1_banner="string",
            alt2_banner="string",
            logo="string",
            contact=config_contact,
            toggles=toggles,
        )

        shop = ShopTable(
            name="Test Shop with config",
            description="Test Shop Description with config",
            config=config.model_dump(),
            shop_type="{}",
            vat_standard=21,
            vat_lower_1=15,
            vat_lower_2=10,
            vat_lower_3=5,
            vat_special=2,
            vat_zero=0,
            stripe_public_key="string",
        )
    else:
        shop = ShopTable(
            name="Test Shop",
            description="Test Shop Description",
            stripe_public_key="string",
            vat_standard=21,
            vat_lower_1=15,
            vat_lower_2=10,
            vat_lower_3=5,
            vat_special=2,
            vat_zero=0,
            config="{}",
            shop_type="{}",
        )
    db.session.add(shop)
    db.session.commit()
    return shop.id

"""
add attributes, attribute_options, attribute_translations, product_attribute_values

Revision ID: a1b2c3d4e5f6
Revises: 18a302939a23
Create Date: 2026-01-23 13:07:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "cac5979b07e9"
branch_labels = None
depends_on = None


def upgrade() -> None:

    # attributes
    op.create_table(
        "attributes",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            server_default=sa.text("uuid_generate_v4()"),
            primary_key=True,
            index=True,
        ),
        sa.Column("shop_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("shops.id"), index=True),
        sa.Column("name", sa.String(length=60), index=True, nullable=False),
        sa.Column("unit", sa.String(length=20), nullable=True),
    )
    op.create_unique_constraint("uq_attribute_shop_name", "attributes", ["shop_id", "name"])

    # attribute_translations
    op.create_table(
        "attribute_translations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            server_default=sa.text("uuid_generate_v4()"),
            primary_key=True,
            index=True,
        ),
        sa.Column("attribute_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("attributes.id")),
        sa.Column("main_name", sa.String(length=100), nullable=False),
        sa.Column("alt1_name", sa.String(length=100), nullable=True),
        sa.Column("alt2_name", sa.String(length=100), nullable=True),
    )
    op.create_index("ix_attribute_translations_main_name", "attribute_translations", ["main_name"])
    op.create_index("ix_attribute_translations_alt1_name", "attribute_translations", ["alt1_name"])
    op.create_index("ix_attribute_translations_alt2_name", "attribute_translations", ["alt2_name"])

    # attribute_options
    op.create_table(
        "attribute_options",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            server_default=sa.text("uuid_generate_v4()"),
            primary_key=True,
            index=True,
        ),
        sa.Column("attribute_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("attributes.id"), index=True),
        sa.Column("value_key", sa.String(length=60), nullable=False, index=True),
    )
    op.create_unique_constraint("uq_attribute_option_key", "attribute_options", ["attribute_id", "value_key"])

    # product_attribute_values
    op.create_table(
        "product_attribute_values",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            server_default=sa.text("uuid_generate_v4()"),
            primary_key=True,
            index=True,
        ),
        sa.Column("product_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("products.id"), index=True),
        sa.Column("attribute_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("attributes.id"), index=True),
        sa.Column(
            "option_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("attribute_options.id"),
            nullable=True,
            index=True,
        ),
    )
    op.create_unique_constraint(
        "uq_pav_product_attribute_option_value",
        "product_attribute_values",
        ["product_id", "attribute_id", "option_id"],
    )

    # Helpful partial indexes for filtering
    op.execute(
        "CREATE INDEX IF NOT EXISTS pav_attr_option_idx ON product_attribute_values(attribute_id, option_id) WHERE option_id IS NOT NULL;"
    )


def downgrade() -> None:
    # Drop partial indexes
    op.execute("DROP INDEX IF EXISTS pav_attr_value_idx;")
    op.execute("DROP INDEX IF EXISTS pav_attr_option_idx;")

    # Drop tables in reverse order
    op.drop_constraint("uq_pav_product_attribute_option_value", "product_attribute_values", type_="unique")
    op.drop_table("product_attribute_values")

    op.drop_constraint("uq_attribute_option_key", "attribute_options", type_="unique")
    op.drop_table("attribute_options")

    op.drop_index("ix_attribute_translations_alt2_name", table_name="attribute_translations")
    op.drop_index("ix_attribute_translations_alt1_name", table_name="attribute_translations")
    op.drop_index("ix_attribute_translations_main_name", table_name="attribute_translations")
    op.drop_table("attribute_translations")

    op.drop_constraint("uq_attribute_shop_name", "attributes", type_="unique")
    op.drop_table("attributes")

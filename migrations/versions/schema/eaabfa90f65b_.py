"""Add default data : flavors and tags/effects

Revision ID: eaabfa90f65b
Revises: 75c79b52c3b4
Create Date: 2019-09-07 00:54:25.753103

"""

import uuid

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "eaabfa90f65b"
down_revision = "75c79b52c3b4"
branch_labels = None
depends_on = None


TAGS = [
    "Anxious",
    "Aroused",
    "Creative",
    "Energetic",
    "Euphoric",
    "Sleepy",
    "Talkative",
    "Tingly",
    "Uplifted",
    "Relaxed",
    "Focused",
    "Giggly",
    "Happy",
    "Hungry",
]
FLAVORS = [
    "Ammonia",
    "Apple",
    "Apricot",
    "Berry",
    "Blue Cheese",
    "Blueberry",
    "Butter",
    "Cheese",
    "Chemical",
    "Chestnut",
    "Citrus",
    "Coffee",
    "Diesel",
    "Earthy",
    "Flowery",
    "Grape",
    "Grapefruit",
    "Honey",
    "Lavender",
    "Lemon",
    "Lime",
    "Mango",
    "Menthol",
    "Mint",
    "Nutty",
    "Orange",
    "Peach",
    "Pear",
    "Pepper",
    "Tobacco",
    "Tree Fruit",
    "Tropical",
    "Vanilla",
    "Violet",
    "Woody",
    "Tea",
    "Pine",
    "Pineapple",
    "Plum",
    "Pungent",
    "Rose",
    "Sage",
    "Skunk",
    "Spicy/Herbal",
    "Strawberry",
    "Sweet",
    "Tar",
]


def add_flavor(conn, name):
    conn.execute(
        sa.text(
            """INSERT INTO flavors (id, name, icon)
               VALUES (:id, :name, :icon)"""
        ),
        id=uuid.uuid4(),
        name=name,
        icon=name.lower(),
    )


def add_tag(conn, name):
    conn.execute(
        sa.text(
            """INSERT INTO tags (id, name)
               VALUES (:id, :name)"""
        ),
        id=uuid.uuid4(),
        name=name,
    )


def upgrade():
    conn = op.get_bind()
    for name in TAGS:
        add_tag(conn, name)
    for name in FLAVORS:
        add_flavor(conn, name)


def downgrade():
    pass

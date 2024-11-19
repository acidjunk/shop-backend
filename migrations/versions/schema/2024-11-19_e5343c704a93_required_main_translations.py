"""required main translations.

Revision ID: e5343c704a93
Revises: 165126b5951e
Create Date: 2024-11-19 15:03:58.903785

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'e5343c704a93'
down_revision = '165126b5951e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('category_translations', 'main_name',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.alter_column('category_translations', 'main_description',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('product_translations', 'main_name',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.alter_column('product_translations', 'main_description',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('product_translations', 'main_description_short',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('tag_translations', 'main_name',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tag_translations', 'main_name',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
    op.alter_column('product_translations', 'main_description_short',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('product_translations', 'main_description',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('product_translations', 'main_name',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.alter_column('category_translations', 'main_description',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('category_translations', 'main_name',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    # ### end Alembic commands ###

"""Add name hash.

Revision ID: 5fc9da366ad7
Revises: 7ae482eb2f95
Create Date: 2024-07-19 16:14:01.610197

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '5fc9da366ad7'
down_revision = '7ae482eb2f95'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('accounts', sa.Column('hash_name', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_accounts_hash_name'), 'accounts', ['hash_name'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_accounts_hash_name'), table_name='accounts')
    op.drop_column('accounts', 'hash_name')
    # ### end Alembic commands ###

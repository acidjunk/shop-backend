"""Create early access table.

Revision ID: b7c94f40743f
Revises: e01e0b0ee64a
Create Date: 2025-03-25 11:43:54.537235

"""
import sqlalchemy as sa
from alembic import op

import sqlalchemy_utils
from server.db.models import UtcTimestamp



# revision identifiers, used by Alembic.
revision = 'b7c94f40743f'
down_revision = 'e01e0b0ee64a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('early_access',
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('created_at', UtcTimestamp(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_early_access_id'), 'early_access', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_early_access_id'), table_name='early_access')
    op.drop_table('early_access')
    # ### end Alembic commands ###

"""Initial scheme.

Revision ID: c57ec832538d
Revises: 
Create Date: 2024-05-03 11:56:43.970374

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'c57ec832538d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('products',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('image_1', sa.String(length=255), nullable=True),
    sa.Column('image_2', sa.String(length=255), nullable=True),
    sa.Column('image_3', sa.String(length=255), nullable=True),
    sa.Column('image_4', sa.String(length=255), nullable=True),
    sa.Column('image_5', sa.String(length=255), nullable=True),
    sa.Column('image_6', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)
    op.create_index(op.f('ix_products_image_1'), 'products', ['image_1'], unique=True)
    op.create_index(op.f('ix_products_image_2'), 'products', ['image_2'], unique=True)
    op.create_index(op.f('ix_products_image_3'), 'products', ['image_3'], unique=True)
    op.create_index(op.f('ix_products_image_4'), 'products', ['image_4'], unique=True)
    op.create_index(op.f('ix_products_image_5'), 'products', ['image_5'], unique=True)
    op.create_index(op.f('ix_products_image_6'), 'products', ['image_6'], unique=True)
    op.create_table('role',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_role_id'), 'role', ['id'], unique=False)
    op.create_table('shops',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('allowed_ips', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('description')
    )
    op.create_index(op.f('ix_shops_id'), 'shops', ['id'], unique=False)
    op.create_index(op.f('ix_shops_name'), 'shops', ['name'], unique=True)
    op.create_table('user',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('first_name', sa.String(length=255), nullable=True),
    sa.Column('last_name', sa.String(length=255), nullable=True),
    sa.Column('username', sa.String(length=255), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('fs_uniquifier', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('confirmed_at', sa.DateTime(), nullable=True),
    sa.Column('mail_offers', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_user_first_name'), 'user', ['first_name'], unique=False)
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)
    op.create_index(op.f('ix_user_last_name'), 'user', ['last_name'], unique=False)
    op.create_table('accounts',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('shop_id', sa.UUID(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['shop_id'], ['shops.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_accounts_id'), 'accounts', ['id'], unique=False)
    op.create_index(op.f('ix_accounts_shop_id'), 'accounts', ['shop_id'], unique=False)
    op.create_table('categories',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('color', sa.String(length=20), nullable=True),
    sa.Column('icon', sa.String(length=100), nullable=True),
    sa.Column('shop_id', sa.UUID(), nullable=True),
    sa.Column('order_number', sa.Integer(), nullable=True),
    sa.Column('image_1', sa.String(length=255), nullable=True),
    sa.Column('image_2', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['shop_id'], ['shops.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
    op.create_index(op.f('ix_categories_image_1'), 'categories', ['image_1'], unique=True)
    op.create_index(op.f('ix_categories_image_2'), 'categories', ['image_2'], unique=True)
    op.create_index(op.f('ix_categories_shop_id'), 'categories', ['shop_id'], unique=False)
    op.create_table('product_translations',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('product_id', sa.UUID(), nullable=True),
    sa.Column('main_name', sa.String(length=255), nullable=True),
    sa.Column('main_description', sa.String(), nullable=True),
    sa.Column('main_description_short', sa.String(), nullable=True),
    sa.Column('alt1_name', sa.String(length=255), nullable=True),
    sa.Column('alt1_description', sa.String(), nullable=True),
    sa.Column('alt1_description_short', sa.String(), nullable=True),
    sa.Column('alt2_name', sa.String(length=255), nullable=True),
    sa.Column('alt2_description', sa.String(), nullable=True),
    sa.Column('alt2_description_short', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_translations_alt1_description'), 'product_translations', ['alt1_description'], unique=True)
    op.create_index(op.f('ix_product_translations_alt1_description_short'), 'product_translations', ['alt1_description_short'], unique=True)
    op.create_index(op.f('ix_product_translations_alt1_name'), 'product_translations', ['alt1_name'], unique=True)
    op.create_index(op.f('ix_product_translations_alt2_description'), 'product_translations', ['alt2_description'], unique=True)
    op.create_index(op.f('ix_product_translations_alt2_description_short'), 'product_translations', ['alt2_description_short'], unique=True)
    op.create_index(op.f('ix_product_translations_alt2_name'), 'product_translations', ['alt2_name'], unique=True)
    op.create_index(op.f('ix_product_translations_id'), 'product_translations', ['id'], unique=False)
    op.create_index(op.f('ix_product_translations_main_description'), 'product_translations', ['main_description'], unique=True)
    op.create_index(op.f('ix_product_translations_main_description_short'), 'product_translations', ['main_description_short'], unique=True)
    op.create_index(op.f('ix_product_translations_main_name'), 'product_translations', ['main_name'], unique=True)
    op.create_table('roles_users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=True),
    sa.Column('role_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('shops_users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=True),
    sa.Column('shop_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['shop_id'], ['shops.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shops_users_id'), 'shops_users', ['id'], unique=False)
    op.create_table('tags',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('shop_id', sa.UUID(), nullable=True),
    sa.Column('name', sa.String(length=60), nullable=True),
    sa.ForeignKeyConstraint(['shop_id'], ['shops.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tags_id'), 'tags', ['id'], unique=False)
    op.create_index(op.f('ix_tags_name'), 'tags', ['name'], unique=True)
    op.create_index(op.f('ix_tags_shop_id'), 'tags', ['shop_id'], unique=False)
    op.create_table('category_translations',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('category_id', sa.UUID(), nullable=True),
    sa.Column('main_name', sa.String(length=255), nullable=True),
    sa.Column('main_description', sa.String(), nullable=True),
    sa.Column('alt1_name', sa.String(length=255), nullable=True),
    sa.Column('alt1_description', sa.String(), nullable=True),
    sa.Column('alt2_name', sa.String(length=255), nullable=True),
    sa.Column('alt2_description', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_category_translations_alt1_description'), 'category_translations', ['alt1_description'], unique=True)
    op.create_index(op.f('ix_category_translations_alt1_name'), 'category_translations', ['alt1_name'], unique=True)
    op.create_index(op.f('ix_category_translations_alt2_description'), 'category_translations', ['alt2_description'], unique=True)
    op.create_index(op.f('ix_category_translations_alt2_name'), 'category_translations', ['alt2_name'], unique=True)
    op.create_index(op.f('ix_category_translations_id'), 'category_translations', ['id'], unique=False)
    op.create_index(op.f('ix_category_translations_main_description'), 'category_translations', ['main_description'], unique=True)
    op.create_index(op.f('ix_category_translations_main_name'), 'category_translations', ['main_name'], unique=True)
    op.create_table('orders',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('customer_order_id', sa.Integer(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.Column('shop_id', sa.UUID(), nullable=True),
    sa.Column('account_id', sa.UUID(), nullable=True),
    sa.Column('order_info', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
    sa.ForeignKeyConstraint(['shop_id'], ['shops.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)
    op.create_index(op.f('ix_orders_shop_id'), 'orders', ['shop_id'], unique=False)
    op.create_table('products_to_tags',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('shop_id', sa.UUID(), nullable=True),
    sa.Column('product_id', sa.UUID(), nullable=True),
    sa.Column('tag_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.ForeignKeyConstraint(['shop_id'], ['shops.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_to_tags_id'), 'products_to_tags', ['id'], unique=False)
    op.create_index(op.f('ix_products_to_tags_product_id'), 'products_to_tags', ['product_id'], unique=False)
    op.create_index(op.f('ix_products_to_tags_shop_id'), 'products_to_tags', ['shop_id'], unique=False)
    op.create_index(op.f('ix_products_to_tags_tag_id'), 'products_to_tags', ['tag_id'], unique=False)
    op.create_table('tag_translations',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tag_id', sa.UUID(), nullable=True),
    sa.Column('main_name', sa.String(length=100), nullable=True),
    sa.Column('alt1_name', sa.String(length=100), nullable=False),
    sa.Column('alt2_name', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tag_translations_alt1_name'), 'tag_translations', ['alt1_name'], unique=True)
    op.create_index(op.f('ix_tag_translations_alt2_name'), 'tag_translations', ['alt2_name'], unique=True)
    op.create_index(op.f('ix_tag_translations_id'), 'tag_translations', ['id'], unique=False)
    op.create_index(op.f('ix_tag_translations_main_name'), 'tag_translations', ['main_name'], unique=True)
    op.create_table('licenses',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('is_recurring', sa.Boolean(), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.Column('improviser_user', sa.UUID(), nullable=False),
    sa.Column('seats', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_licenses_id'), 'licenses', ['id'], unique=False)
    op.create_index(op.f('ix_licenses_order_id'), 'licenses', ['order_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_licenses_order_id'), table_name='licenses')
    op.drop_index(op.f('ix_licenses_id'), table_name='licenses')
    op.drop_table('licenses')
    op.drop_index(op.f('ix_tag_translations_main_name'), table_name='tag_translations')
    op.drop_index(op.f('ix_tag_translations_id'), table_name='tag_translations')
    op.drop_index(op.f('ix_tag_translations_alt2_name'), table_name='tag_translations')
    op.drop_index(op.f('ix_tag_translations_alt1_name'), table_name='tag_translations')
    op.drop_table('tag_translations')
    op.drop_index(op.f('ix_products_to_tags_tag_id'), table_name='products_to_tags')
    op.drop_index(op.f('ix_products_to_tags_shop_id'), table_name='products_to_tags')
    op.drop_index(op.f('ix_products_to_tags_product_id'), table_name='products_to_tags')
    op.drop_index(op.f('ix_products_to_tags_id'), table_name='products_to_tags')
    op.drop_table('products_to_tags')
    op.drop_index(op.f('ix_orders_shop_id'), table_name='orders')
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_table('orders')
    op.drop_index(op.f('ix_category_translations_main_name'), table_name='category_translations')
    op.drop_index(op.f('ix_category_translations_main_description'), table_name='category_translations')
    op.drop_index(op.f('ix_category_translations_id'), table_name='category_translations')
    op.drop_index(op.f('ix_category_translations_alt2_name'), table_name='category_translations')
    op.drop_index(op.f('ix_category_translations_alt2_description'), table_name='category_translations')
    op.drop_index(op.f('ix_category_translations_alt1_name'), table_name='category_translations')
    op.drop_index(op.f('ix_category_translations_alt1_description'), table_name='category_translations')
    op.drop_table('category_translations')
    op.drop_index(op.f('ix_tags_shop_id'), table_name='tags')
    op.drop_index(op.f('ix_tags_name'), table_name='tags')
    op.drop_index(op.f('ix_tags_id'), table_name='tags')
    op.drop_table('tags')
    op.drop_index(op.f('ix_shops_users_id'), table_name='shops_users')
    op.drop_table('shops_users')
    op.drop_table('roles_users')
    op.drop_index(op.f('ix_product_translations_main_name'), table_name='product_translations')
    op.drop_index(op.f('ix_product_translations_main_description_short'), table_name='product_translations')
    op.drop_index(op.f('ix_product_translations_main_description'), table_name='product_translations')
    op.drop_index(op.f('ix_product_translations_id'), table_name='product_translations')
    op.drop_index(op.f('ix_product_translations_alt2_name'), table_name='product_translations')
    op.drop_index(op.f('ix_product_translations_alt2_description_short'), table_name='product_translations')
    op.drop_index(op.f('ix_product_translations_alt2_description'), table_name='product_translations')
    op.drop_index(op.f('ix_product_translations_alt1_name'), table_name='product_translations')
    op.drop_index(op.f('ix_product_translations_alt1_description_short'), table_name='product_translations')
    op.drop_index(op.f('ix_product_translations_alt1_description'), table_name='product_translations')
    op.drop_table('product_translations')
    op.drop_index(op.f('ix_categories_shop_id'), table_name='categories')
    op.drop_index(op.f('ix_categories_image_2'), table_name='categories')
    op.drop_index(op.f('ix_categories_image_1'), table_name='categories')
    op.drop_index(op.f('ix_categories_id'), table_name='categories')
    op.drop_table('categories')
    op.drop_index(op.f('ix_accounts_shop_id'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_id'), table_name='accounts')
    op.drop_table('accounts')
    op.drop_index(op.f('ix_user_last_name'), table_name='user')
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_index(op.f('ix_user_first_name'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_shops_name'), table_name='shops')
    op.drop_index(op.f('ix_shops_id'), table_name='shops')
    op.drop_table('shops')
    op.drop_index(op.f('ix_role_id'), table_name='role')
    op.drop_table('role')
    op.drop_index(op.f('ix_products_image_6'), table_name='products')
    op.drop_index(op.f('ix_products_image_5'), table_name='products')
    op.drop_index(op.f('ix_products_image_4'), table_name='products')
    op.drop_index(op.f('ix_products_image_3'), table_name='products')
    op.drop_index(op.f('ix_products_image_2'), table_name='products')
    op.drop_index(op.f('ix_products_image_1'), table_name='products')
    op.drop_index(op.f('ix_products_id'), table_name='products')
    op.drop_table('products')
    # ### end Alembic commands ###

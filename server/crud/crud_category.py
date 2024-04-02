from typing import Optional
from uuid import UUID

from server.crud.base import CRUDBase
from server.db.models import Category
from server.schemas.category import CategoryCreate, CategoryUpdate


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    def get_by_name(self, *, name: str, shop_id: UUID) -> Optional[Category]:
        return Category.query.filter(Category.name == name).filter(Category.shop_id == shop_id).first()


category_crud = CRUDCategory(Category)

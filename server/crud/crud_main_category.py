from server.crud.base import CRUDBase
from server.db.models import MainCategory
from server.schemas.main_category import MainCategoryCreate, MainCategoryUpdate


class CRUDMainCategory(CRUDBase[MainCategory, MainCategoryCreate, MainCategoryUpdate]):
    pass


main_category_crud = CRUDMainCategory(MainCategory)

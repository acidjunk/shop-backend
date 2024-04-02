from typing import Any, List, Optional
from uuid import UUID

import structlog
from pydantic import conlist, validator
from pydantic.class_validators import root_validator

from server.db.models import Category, Kind, MainCategory, ProductsTable, Strain, Tag
from server.pydantic_forms.core import DisplayOnlyFieldType, FormPage, ReadOnlyField, register_form
from server.pydantic_forms.types import AcceptItemType, FormGenerator, State, SummaryData
from server.pydantic_forms.validators import Choice, ListOfTwo, LongText, MarkdownText, MigrationSummary, Timestamp

logger = structlog.get_logger(__name__)


class Hidden(DisplayOnlyFieldType):
    @classmethod
    def __modify_schema__(cls, field_schema: dict[str, Any]) -> None:
        field_schema.update(format="hidden", type="string")


def validate_product_name(product_name: str, values: State) -> str:
    """Check if product already exists."""
    products = ProductsTable.query.all()
    product_items = [item.name.lower() for item in products]
    if product_name.lower() in product_items:
        raise ValueError("Dit product bestaat al.")
    return product_name


def validate_category_name(category_name: str, values: State) -> str:
    """Check if category already exists."""
    categories = Category.query.filter(Category.shop_id == values["shop_id"]).all()
    category_items = [item.name.lower() for item in categories]
    if category_name.lower() in category_items:
        raise ValueError("Deze categorie bestaat al.")
    return category_name


def validate_strain_name(strain_name: str, values: State) -> str:
    """Check if strain already exists."""
    strains = Strain.query.all()
    strain_items = [item.name.lower() for item in strains]
    if strain_name.lower() in strain_items:
        raise ValueError("Deze kruising bestaat al.")
    return strain_name


def validate_multiple_strains(strain_names: List[str], values: State) -> List[str]:
    """Check if strains already exist."""
    strains = Strain.query.all()
    strain_items = [item.name.lower() for item in strains]

    invalid_strains = []

    for strain_name in strain_names:
        if strain_name.lower() in strain_items:
            invalid_strains.append(strain_name)

    if invalid_strains:
        raise ValueError(f"The following strains already exist: {', '.join(invalid_strains)}")

    return strain_names


def validate_combined_strains(cls, values):
    # If the value the same as its default value it returns None
    new_strain = (
        values.get("new_strain_from_name")
        if values.get("new_strain_from_name") is not None
        else cls.Config.new_strain_from_name_default
    )
    strain_count = len(values.get("strain_choice", [])) + len(values.get("create_new_strains", []))

    description_nl = values.get("product_description_nl") if values.get("product_description_nl") is not "" else None
    description_en = values.get("product_description_en") if values.get("product_description_en") is not "" else None
    has_full_description = bool(description_nl and description_en)

    if (strain_count == 0) and not new_strain and not has_full_description:
        raise ValueError(f'At least 1 strain required or check "New strain from name" or add EN/NL Descriptions')

    return values


def validate_tag_name(tag_name: str, values: State) -> str:
    """Check if tag already exists."""
    tags = Tag.query.all()
    tag_items = [item.name.lower() for item in tags]
    if tag_name.lower() in tag_items:
        raise ValueError("Deze tag bestaat al.")
    return tag_name


def validate_kind_name(kind_name: str, values: State) -> str:
    """Check if kind already exists."""
    kinds = Kind.query.all()
    kind_items = [item.name.lower() for item in kinds]
    if kind_name.lower() in kind_items:
        raise ValueError("Deze kind bestaat al.")
    return kind_name


def create_strain_form(current_state: dict) -> FormGenerator:
    class StrainForm(FormPage):
        class Config:
            title = "Nieuwe kruising toevoegen"

        strain_name: str
        _validate_strain_name: classmethod = validator("strain_name", allow_reuse=True)(validate_strain_name)

    user_input = yield StrainForm
    return user_input.dict()


def create_tag_form(current_state: dict) -> FormGenerator:
    class TagForm(FormPage):
        class Config:
            title = "Nieuwe tag toevoegen"

        tag_name: str
        _validate_tag_name: classmethod = validator("tag_name", allow_reuse=True)(validate_tag_name)

    user_input = yield TagForm
    return user_input.dict()


class KindType(Choice):
    """Product type as used in the create product form."""

    C = "CBD"
    H = "Hybrid"
    I = "Indica"
    S = "Sativa"


# class MainCategoryChoice(Choice):


def create_kind_to_strains_form(current_state: dict) -> FormGenerator:
    # Setup summary
    summary_fields = [
        "kind_name",
        "kind_type",
    ]
    summary_labels = ["Wiet naam", "type"]

    def summary_data(user_input: dict[str, Any]) -> SummaryData:
        return {
            "labels": summary_labels,
            "columns": [[str(user_input[nm]) for nm in summary_fields]],
        }

    strains = Strain.query.all()

    StrainChoice = Choice(
        "StrainChoice",
        zip(
            [str(strain.id) for strain in strains],
            [(str(strain.id), strain.name) for strain in strains],
        ),  # type: ignore
    )

    # Todo: in future this could be implemented to pre-select a category in price template form
    # categories = Category.query.filter(Category.shop_id == UUID("19149768-691c-40d8-a08e-fe900fd23bc0")).all()
    #
    # CategoryChoice = Choice(
    #     "CategoryChoice",
    #     zip(
    #         [str(category.id) for category in categories],
    #         [(category.name, category.name) for category in categories],
    #     ),  # type: ignore
    # )

    class KindStrainsCategoriesForm(FormPage):
        class Config:
            title = "Nieuw cannabis product"
            new_strain_from_name_default = True
            gebruiken_default = True

        kind_name: str
        kind_type: KindType
        kind_description_nl: Optional[LongText]
        kind_description_en: Optional[LongText]
        strain_choice: conlist(StrainChoice, min_items=0, max_items=3)
        create_new_strains: conlist(str, min_items=0, max_items=3, unique_items=True)
        new_strain_from_name: bool = Config.new_strain_from_name_default
        gebruiken: bool = Config.gebruiken_default

        _validate_kind_name: classmethod = validator("kind_name", allow_reuse=True)(validate_kind_name)
        _validate_multiple_strains: classmethod = validator("create_new_strains", allow_reuse=True)(
            validate_multiple_strains
        )
        _validate_strains: classmethod = root_validator(pre=True, allow_reuse=True)(validate_combined_strains)

    user_input = yield KindStrainsCategoriesForm
    user_input_dict = user_input.dict()

    class SummaryForm(FormPage):
        class Config:
            title = "Samenvatting"

        class Summary(MigrationSummary):
            data = summary_data(user_input_dict)

        summary: Summary
        warning: str = ReadOnlyField(
            "Je kan (nog) geen producten bewerken. Zie je nu een 'typo' ga dan terug naar het vorige formulier en pas het aan."
        )

    _ = yield SummaryForm

    return user_input_dict


def create_kind_form(current_state: dict) -> FormGenerator:
    class KindForm(FormPage):
        class Config:
            title = "Nieuwe cannabis soort toevoegen"

        kind_name: str
        _validate_kind_name: classmethod = validator("kind_name", allow_reuse=True)(validate_kind_name)
        short_description_nl: str
        description_nl: Optional[MarkdownText]
        short_description_en: Optional[str]
        description_en: Optional[MarkdownText]
        kind_type: KindType

    user_input = yield KindForm
    return user_input.dict()


def create_product_form(current_state: dict) -> FormGenerator:
    class ProductForm(FormPage):
        class Config:
            title = "Nieuwe horeca product toevoegen"

        product_name: str
        _validate_product_name: classmethod = validator("product_name", allow_reuse=True)(validate_product_name)
        short_description_nl: str
        description_nl: Optional[MarkdownText]
        short_description_en: Optional[str]
        description_en: Optional[MarkdownText]

    user_input = yield ProductForm
    return user_input.dict()


def create_category_form(current_state: dict) -> FormGenerator:
    main_categories = MainCategory.query.filter(MainCategory.shop_id == current_state["extra_state"]["shop_id"]).all()

    MainCategoryChoice = Choice(
        "MainCategoryChoice",
        zip(
            [str(main_category.id) for main_category in main_categories],
            [(str(main_category.id), main_category.name) for main_category in main_categories],
        ),  # type: ignore
    )

    class CategoryForm(FormPage):
        class Config:
            title = "Nieuwe categorie toevoegen"

        shop_id: Hidden = current_state["extra_state"]["shop_id"]
        category_name: str
        _validate_category_name: classmethod = validator("category_name", allow_reuse=True)(validate_category_name)
        name_en: Optional[str]
        # description: Optional[str]
        main_category_id: MainCategoryChoice
        color: str = "#000000"
        icon: Optional[str]
        is_cannabis: bool = False

    user_input = yield CategoryForm
    return user_input.dict()


register_form("create_kind_to_strains_form", create_kind_to_strains_form)
register_form("create_strain_form", create_strain_form)
register_form("create_tag_form", create_tag_form)
register_form("create_kind_form", create_kind_form)
register_form("create_product_form", create_product_form)
register_form("create_categorie_form", create_category_form)

from http import HTTPStatus
from typing import Annotated, Any, ClassVar, Iterator
from annotated_types import (
    Ge,
    Le,
    MultipleOf,
    Predicate
)

import structlog
from fastapi import APIRouter, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.param_functions import Body
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from pydantic_forms.core import post_form
from pydantic_forms.core import FormPage as PydanticFormsFormPage
from pydantic_forms.types import JSON, State
from pydantic_forms.validators import (
    LongText,
    Label,
    Divider,
    Hidden,
    Choice,
    choice_list,
)
from sqlalchemy.exc import IntegrityError

from server.crud.crud_info_request import info_request_crud
from server.crud.crud_product import product_crud
from server.schemas.info_request import InfoRequestCreate
from server.utils.discord.discord import post_discord_info_request
from server.utils.discord.settings import co2_shop_settings

logger = structlog.get_logger(__name__)

router = APIRouter()


class FormPage(PydanticFormsFormPage):
    meta__: ClassVar[JSON] = {"hasNext": True}


class SubmitFormPage(FormPage):
    meta__: ClassVar[JSON] = {"hasNext": False}


def example_backend_validation(val: int) -> bool:
    if val == 9:
        raise ValueError("Value cannot be 9")
    return True


NumberExample = Annotated[
    int, Ge(1), Le(10), MultipleOf(multiple_of=3), Predicate(example_backend_validation)
]


class DropdownChoices(Choice):
    _1 = ("1", "Option 1")
    _2 = ("2", "Option 2")
    _3 = ("3", "Option 3")
    _4 = ("4", "Option 4")


class RadioChoices(Choice):
    _1 = ("1", "Option 1")
    _2 = ("2", "Option 2")
    _3 = ("3", "Option 3")


class MultiCheckBoxChoices(Choice):
    _1 = ("1", "Option 1")
    _2 = ("2", "Option 2")
    _3 = ("3", "Option 3")
    _4 = ("4", "Option 4")


class ListChoices(Choice):
    _0 = ("0", "Option 0")
    _1 = ("1", "Option 1")
    _2 = ("2", "Option 2")
    _3 = ("3", "Option 3")
    _4 = ("4", "Option 4")
    _5 = ("5", "Option 5")
    _6 = ("6", "Option 6")


class Education(BaseModel):
    degree: str | None
    year: int | None


class Person(BaseModel):
    name: str
    age: Annotated[int, Ge(18), Le(99)]
    education: Education

@router.post("/form")
async def form(form_data: list[dict] = []):
    def form_generator(state: State):
        class TestForm0(FormPage):
            model_config = ConfigDict(title="Form Title Page 0")

            number0: Annotated[int, Ge(18), Le(99)] = 17

        form_data_0 = yield TestForm0

        class TestForm1(FormPage):
            model_config = ConfigDict(title="Form Title Page 1")

            number1: Annotated[int, Ge(18), Le(99)] = 17

        form_data_1 = yield TestForm1

        class TestForm2(FormPage):
            model_config = ConfigDict(title="Form Title Page 2")

            number: NumberExample = 3
            text: Annotated[str, Field(min_length=3, max_length=12)] = "Default text"
            textArea: LongText = "Text area default"
            divider: Divider
            label: Label = "Label"
            hidden: Hidden = "Hidden"
            # When there are > 3 choices a dropdown will be rendered
            dropdown: DropdownChoices = "2"
            # When there are <= 3 choices a radio group will be rendered
            radio: RadioChoices = "3"
            #  checkbox: bool = True TODO: Fix validation errors on this

            # When there are <= 5 choices in a list a set of checkboxes are rendered
            # multicheckbox: choice_list(MultiCheckBoxChoices, min_items=3) = ["1", "2"]
            # list: choice_list(ListChoices) = [0, 1]

            person: Person

        form_data_2 = yield TestForm2

        class TestSubmitForm(SubmitFormPage):
            model_config = ConfigDict(title="Submit Form")

            name_2: str | None = None

        form_data_submit = yield TestSubmitForm

        return form_data_0.model_dump() |  form_data_1.model_dump() | form_data_2.model_dump() | form_data_submit.model_dump()

    post_form(form_generator, state={}, user_inputs=form_data)
    return "OK!"


@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create_info_request(data: InfoRequestCreate = Body(...)) -> Any:
    try:
        logger.info("Saving early access", data=data)
        info_request = info_request_crud.create(obj_in=data)
        if str(data.shop_id) == "d3c745bc-285f-4810-9612-6fbb8a84b125":
            product = product_crud.get_id_by_shop_id(data.shop_id, data.product_id)
            post_discord_info_request(
                f"New info request from {data.email} about product: {product.translation.main_name}",
                settings=co2_shop_settings,
                email=data.email,
                product_name=product.translation.main_name,
                product_id=data.product_id,
            )
        return info_request

    except ValidationError as ve:
        # Log the validation error
        logger.error("Validation error occurred", error=str(ve), data=data)
        # Raise 422 for incorrect input format
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="Incorrect input format or missing fields in the request.",
        )

    except IntegrityError as ie:
        # Log the duplicate entry error
        logger.error("Duplicate entry error", error=str(ie), data=data)
        # Raise 409 for duplicate entry (e.g., unique constraint violation)
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Duplicate entry. The record already exists.",
        )

    except RequestValidationError as rve:
        # Log the 400 Bad Request error
        logger.error("Bad request error", error=str(rve), data=data)
        # Raise 400 for bad requests (malformed or incomplete data)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Malformed request or invalid data.",
        )

    except Exception as e:
        # Log the unexpected error
        logger.error("Unexpected error occurred", error=str(e), data=data)
        # Raise 500 for unexpected errors
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )

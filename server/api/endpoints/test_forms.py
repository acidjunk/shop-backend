from typing import Annotated, ClassVar

import structlog
from annotated_types import Predicate
from fastapi import APIRouter
from pydantic import ConfigDict, EmailStr, Field
from pydantic_forms.core import FormPage
from pydantic_forms.core import FormPage as PydanticFormsFormPage
from pydantic_forms.core import post_form
from pydantic_forms.types import JSON, State
from pydantic_forms.validators import Choice, unique_conlist

logger = structlog.get_logger(__name__)

router = APIRouter()


class FormPage(PydanticFormsFormPage):
    meta__: ClassVar[JSON] = {"hasNext": True}


class SubmitFormPage(FormPage):
    meta__: ClassVar[JSON] = {"hasNext": False}


def example_list_validation(val: int) -> bool:
    return True


TestExampleNumberList = Annotated[
    unique_conlist(int, min_items=2, max_items=5),
    Predicate(example_list_validation),
]


class ListChoices(Choice):
    _0 = ("0", "Option 0")
    _1 = ("1", "Option 1")
    _2 = ("2", "Option 2")
    _3 = ("3", "Option 3")
    _4 = ("4", "Option 4")
    _5 = ("5", "Option 5")
    _6 = ("6", "Option 6")


TestString = Annotated[str, Field(min_length=2, max_length=10)]


class Person(BaseModel):
    name: str
    age: Annotated[int, Ge(18), Le(99), MultipleOf(multiple_of=3)]
    education: Education


@router.post("/")
async def form(form_data: list[dict] = []):
    def form_generator(state: State):
        class TestForm(FormPage):
            model_config = ConfigDict(title="Form Title Page 1")

            email: EmailStr
            number: int
            check: bool
            # textList: unique_conlist(TestString, min_items=1, max_items=5)
            # numberList: TestExampleNumberList
            select: ListChoices

        form_data_email = yield TestForm

        class SecondForm(FormPage):
            # todo; check if it works without a title.
            discover_date: datetime
            names: list[str]
            persons: list[Person]

        form_second = yield SecondForm

        return form_data_email.model_dump()

    post_form(form_generator, state={}, user_inputs=form_data)

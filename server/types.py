# Copyright 2024 René Dohmen <acidjunk@gmail.com>
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum
from http import HTTPStatus
from typing import Any, Callable, Dict, Generator, List, Literal, Optional, Tuple, Type, TypedDict, TypeVar, Union

from pydantic import BaseModel, EmailStr

UUIDstr = str
State = Dict[str, Any]
JSON = Any
# ErrorState is either a string containing an error message, a catched Exception or a tuple containing a message and
# a HTTP status code
ErrorState = Union[str, Exception, Tuple[str, Union[int, HTTPStatus]]]
# An ErrorDict should have the following keys:
# error: str  # A message describing the error
# class: str[Optional]  # The exception class name (type)
# status_code: Optional[int]  # HTTP Status code (optional)
# traceback: Optional[str]  # A python traceback as a string formatted by nwastdlib.ex.show_ex
ErrorDict = Dict[str, Union[str, int, List[Dict[str, Any]], "InputForm", None]]
StateStepFunc = Callable[[State], State]
StepFunc = Callable[..., Optional[State]]


class strEnum(str, Enum):
    def __str__(self) -> str:
        return self.value

    @classmethod
    def values(cls) -> List:
        return list(map(lambda obj: obj.value, cls))  # type: ignore


class AcceptItemType(strEnum):
    INFO = "info"
    LABEL = "label"
    WARNING = "warning"
    URL = "url"
    CHECKBOX = "checkbox"
    SUBCHECKBOX = ">checkbox"
    OPTIONAL_CHECKBOX = "checkbox?"
    OPTIONAL_SUBCHECKBOX = ">checkbox?"
    SKIP = "skip"
    VALUE = "value"
    MARGIN = "margin"


AcceptData = List[Union[Tuple[str, AcceptItemType], Tuple[str, AcceptItemType, Dict]]]


class SummaryData(TypedDict, total=False):
    headers: List[str]
    labels: List[str]
    columns: List[List[Union[str, int, bool, float]]]


class MailAddress(TypedDict):
    email: EmailStr
    name: str


class ConfirmationMail(TypedDict):
    message: str
    subject: str
    language: str
    to: List[MailAddress]
    cc: List[MailAddress]


InputForm = Type[BaseModel]

T = TypeVar("T", bound=BaseModel)
FormGenerator = Generator[Type[T], T, State]
SimpleInputFormGenerator = Callable[..., InputForm]
InputFormGenerator = Callable[..., FormGenerator]
InputStepFunc = Union[SimpleInputFormGenerator, InputFormGenerator]
StateSimpleInputFormGenerator = Callable[[State], InputForm]
StateInputFormGenerator = Callable[[State], FormGenerator]
StateInputStepFunc = Union[StateSimpleInputFormGenerator, StateInputFormGenerator]


def is_of_type(t: Any, test_type: Any) -> bool:
    """Check if annotation type is valid for type.

    >>> is_of_type(list, list)
    True
    >>> is_of_type(List[int], List[int])
    True
    >>> is_of_type(strEnum, str)
    True
    >>> is_of_type(strEnum, Enum)
    True
    >>> is_of_type(int, str)
    False
    """

    if (
        hasattr(t, "__origin__")
        and hasattr(test_type, "__origin__")
        and t.__origin__ is test_type.__origin__
        and t.__args__ == test_type.__args__
    ):
        return True

    if test_type is t:
        # Test type is a typing type instance and matches
        return True

    # Workaround for the fact that you can't call issubclass on typing types
    try:
        return issubclass(t, test_type)
    except TypeError:
        return False


def is_list_type(t: Any, test_type: Optional[type] = None) -> bool:
    """Check if `t` is list type.

    And optionally check if the list items are of `test_type`

    >>> is_list_type(List[int])
    True
    >>> is_list_type(Optional[List[int]])
    True
    >>> is_list_type(Optional[List[int]], int)
    True
    >>> is_list_type(Optional[List[int]], str)
    False
    >>> is_list_type(Optional[int])
    False
    >>> is_list_type(List[Tuple[int, int]])
    True
    >>> is_list_type(List[Tuple[int, int]], int)
    False
    >>> is_list_type(List[Tuple[int, int]], Tuple[int, int])
    True
    >>> is_list_type(List[strEnum], Enum)
    True
    >>> is_list_type(int)
    False
    >>> is_list_type(Literal[1,2,3])
    False
    """
    if hasattr(t, "__origin__"):
        if is_optional_type(t):
            for arg in t.__args__:
                if is_list_type(arg, test_type):
                    return True
        elif t.__origin__ == Literal:
            return False  # Literal cannot contain lists see pep 586
        elif issubclass(t.__origin__, list):
            if test_type and t.__args__:
                return is_of_type(t.__args__[0], test_type)
            else:
                return True

    return False


def is_optional_type(t: Any, test_type: Optional[type] = None) -> bool:
    """Check if `t` is optional type (Union[None, ...]).

    And optionally check if T is of `test_type`

    >>> is_optional_type(Optional[int])
    True
    >>> is_optional_type(Union[None, int])
    True
    >>> is_optional_type(Optional[int], int)
    True
    >>> is_optional_type(Optional[int], str)
    False
    >>> is_optional_type(Optional[State], int)
    False
    >>> is_optional_type(Optional[State], State)
    True
    >>> is_optional_type(int)
    False
    """
    if hasattr(t, "__origin__"):
        if t.__origin__ == Union and len(t.__args__) == 2:
            for arg in t.__args__:
                if arg is None.__class__:
                    continue

                if test_type:
                    return is_of_type(arg, test_type)
                else:
                    return True
    return False

from enum import Enum
from typing import NotRequired, TypedDict

from pydantic import EmailStr


class MailType(str, Enum):
    INFO = "INFO"
    ORDER_CONFIRMATION = "ORDER_CONFIRMATION"


class InlineImage(TypedDict):
    cid: str
    filename: str
    subtype: str


class MailAttachment(TypedDict):
    content_type: str
    filename: str
    data: bytes


class MailAddress(TypedDict):
    email: EmailStr
    name: str


class ConfirmationMail(TypedDict):
    message: str
    subject: str
    language: str
    to: list[MailAddress]
    cc: list[MailAddress]
    bcc: list[MailAddress]
    sender: NotRequired[MailAddress]
    images: NotRequired[list[InlineImage]]

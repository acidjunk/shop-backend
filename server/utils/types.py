from enum import Enum
from typing import TypedDict

from pydantic import EmailStr


class MailType(str, Enum):
    INFO = "INFO"


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
    sender: MailAddress

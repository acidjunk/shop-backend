import os
from datetime import datetime
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import singledispatch
from itertools import filterfalse
from smtplib import SMTP
from typing import Any, Callable, NoReturn

import html2text
import jinja2
import structlog

from server.schemas.product import ProductBase
from server.settings import mail_settings, template_environment
from server.utils.date_utils import nowtz

# from formatics.utils.singledispatch import single_dispatch_base
from server.utils.types import ConfirmationMail, InlineImage, MailAddress, MailAttachment, MailType

loader = jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "mail_templates"))

logger = structlog.get_logger(__name__)

BCC: list[MailAddress] = [
    {"email": mail_settings.MAIL_BCC, "name": "BCC"},
]
INFO_LINK = {"uri": mail_settings.MAIL_INFO_LINK, "name": mail_settings.MAIL_INFO_NAME}
IMAGES_SHOP_VIRGE = [
    InlineImage(cid="headerimg", filename="shop_virge.png", subtype="png"),
    InlineImage(cid="bannerimg", filename="shop_virge_banner.png", subtype="png"),
    # jpeg example:
    # InlineImage(cid="bannerimg", filename="shop_virge_banner.png", subtype="jpeg"),
]


def get_template_for_product_summary(filename: str) -> jinja2.Template:
    env = template_environment(loader)
    return env.get_template(
        f"product_types/{filename}",
        globals={
            "generate_product_summary": generate_product_summary,
        },
    )


def single_dispatch_base(func: Callable, value: Any) -> NoReturn:
    registry = func.registry  # type: ignore

    supported_models = ", ".join(map(str, filterfalse(lambda t: t is object, registry.keys())))
    model_type = type(value)
    raise TypeError(
        f"`{func.__name__}` called for unsupported model type {model_type}. "
        f"Supported model types are: {supported_models}"
    )


def _generate_subject(mail_type: MailType, language: str, product: str, shop: str, ticket_id: str | None = None) -> str:
    """Return a subject based on info from the original fourme ticket or return a fallback subject if no fourme info is found.

    Args:
        ticket_id: a ticket ID or not
        mail_type: CREATE, MODIFY, TERMINATE
        model: The subscription Model
        language: English or Dutch

    Returns: a string with an e-mail subject

    """
    ticket_prefix = f"[{ticket_id}] - " if ticket_id else ""

    templates = {
        MailType.INFO: {
            "NL": f"{ticket_prefix}Vraag over {product} van {shop}",
            "EN": f"{ticket_prefix}Question about {product} from {shop}",
        },
    }

    try:
        subject = templates[mail_type][language]
    except KeyError as ke:
        raise ValueError(f"No valid workflow target. {mail_type}") from ke
    logger.debug(
        "Generating an email subject with the following params:",
        subject=subject,
        language=language,
        target=mail_type,
        ticket_id=ticket_id,
    )

    return subject


def send_mail(
    confirmation_mail: ConfirmationMail, attachments: list[MailAttachment] = [], allow_unsupervised: bool = False
) -> MIMEMultipart:
    """

    Send E-mail
    """
    message = make_mime_mail(confirmation_mail, attachments, allow_unsupervised)
    if mail_settings.MAIL_ENABLED:
        logger.debug("Sending an email", message=message)
        mailer = SMTP(host=mail_settings.MAIL_SERVER, port=mail_settings.MAIL_PORT)
        mailer.send_message(message)
    return message


def make_mime_mail(
    confirmation_mail: ConfirmationMail, attachments: list[MailAttachment] = [], allow_unsupervised: bool = False
) -> MIMEMultipart:
    """
    The MIME body has the following structure:
    * mixed
      * alternative
        * plain text
        * related
          * html
          * inline image 1
          * inline image n
      * attachment 1
      * attachment n
    """
    if not confirmation_mail["to"]:
        raise ValueError("No recipients")
    if not (confirmation_mail["bcc"]) and not allow_unsupervised:
        raise ValueError("No CC or BCC list. Unsupervised mailing not advised (yet).")

    plain_text_message = html2text.HTML2Text()
    plain_text_message.unicode_snob = True
    plain_text_message.ignore_emphasis = True
    plain_text_message.single_line_break = True
    plain_text = MIMEText(plain_text_message.handle(confirmation_mail["message"]), _subtype="plain")

    message = MIMEMultipart(_subtype="mixed")

    message_from = confirmation_mail.get("sender", {}).get("email", mail_settings.MAIL_FROM)
    message["From"] = message_from
    message["Sender"] = message_from
    message["Reply-To"] = message_from
    message["Subject"] = confirmation_mail["subject"]
    message["To"] = ",".join([r["email"] for r in confirmation_mail["to"]])
    cc = ",".join([r["email"] for r in confirmation_mail["cc"]])
    if cc:
        message["Cc"] = cc
    bcc = ",".join([r["email"] for r in confirmation_mail["bcc"]])
    if bcc:
        message["Bcc"] = bcc

    related = MIMEMultipart(_subtype="related")
    related.attach(MIMEText(confirmation_mail["message"], _subtype="html"))

    for image in confirmation_mail.get("images", []):
        with open(os.path.join(os.path.dirname(__file__), "mail_templates/images", image["filename"]), "rb") as file:
            data = file.read()
        img = MIMEImage(data, image["subtype"])
        img.add_header("Content-Id", f"<{image['cid']}>")
        img.add_header("Content-Disposition", "inline", filename=image["filename"])
        related.attach(img)

    alternative = MIMEMultipart(_subtype="alternative")
    alternative.attach(plain_text)
    alternative.attach(related)
    message.attach(alternative)
    for attachment in attachments:
        content_type = attachment["content_type"]
        mime_type = content_type.split("/") if "/" in content_type else ("application", "octet-stream")
        part = MIMEBase(*mime_type)
        part.set_payload(attachment["data"])
        encode_base64(part)
        part.set_param("name", attachment["filename"])
        part.add_header("Content-Disposition", "attachment", filename=attachment["filename"])
        message.attach(part)

    return message


def _generate_mail_intro_for_product_info(
    contact_names: str, product: ProductBase, language: str, summary: str, date: datetime
) -> str:
    env = template_environment(loader)
    template_file = "mail_intro_product_info.html.j2"
    template = env.get_template(f"{language.lower()}/{template_file}")
    return template.render(
        subscription=ProductBase.from_orm(product),
        contact_names=contact_names,
        info_link=INFO_LINK,
        summary=summary,
        date=date,
    )


# def _generate_mail_intro_for_create_workflow(
#     contact_names: str, model: SubscriptionModel, language: str, summary: str, date: datetime
# ) -> str:
#     env = template_environment(loader)
#     template_file = "mail_intro_create_workflow.html.j2"
#     template = env.get_template(os.path.join(language.lower(), template_file))
#
#     return template.render(
#         subscription=model.model_dump(),
#         contact_names=contact_names,
#         info_link=INFO_LINK,
#         summary=summary,
#         date=date,
#     )
#
#
# def _generate_mail_intro_for_modify_workflow(
#     contact_names: str, model: SubscriptionModel, language: str, summary: str, date: datetime
# ) -> str:
#     env = template_environment(loader)
#
#     template = env.get_template(os.path.join(language.lower(), "mail_intro_modify_workflow.html.j2"))
#     return template.render(
#         subscription=model.model_dump(),
#         contact_names=contact_names,
#         summary=summary,
#         date=date,
#     )
#
#
# def _generate_mail_intro_for_terminate_workflow(
#     contact_names: str, model: SubscriptionModel, language: str, summary: str
# ) -> str:
#     env = template_environment(loader)
#     template = env.get_template(os.path.join(language.lower(), "mail_intro_terminate_workflow.html.j2"))
#     return template.render(subscription=model.model_dump(), contact_names=contact_names, summary=summary)


def generate_confirmation_mail(
    product: ProductBase,
    mail_type: MailType,
    shop_name: str,
    contacts: list[MailAddress],
    ticket_id: str | None,
    extra_content: str | None = None,
    **kwargs: Any,
) -> ConfirmationMail:
    """Generate the complete product specific confirmation_email dict.

    Specific implementations of this generic function will specify the model types they work on. For
    more info about the confirmation email templates please consult: :ref:`email-confirmation-templates`

    Args:
        contacts: a list with contact info (name + email)
        product: Domain model for which to construct a payload.
        mail_type: INFO
        shop_name: name of the shop
        ticket_id: Optional ticket ID (used in subject)
        extra_content: Adds extra text to the main template
        kwargs: Extra arguments, only to be signature compatible

    Returns:
    ---
        A dictionary which contains `message`, `subject`, `to`, `cc` and `language`

    Raises:
    --
        TypeError: in case a specific implementation could not be found. The domain model it was called for will be part of the error message.
        ValueError: in case error occurred whilst determining the recipients or during the generation of the message or subject.
    """
    # Todo: Decide if language support is "generic", we only have dutch customer now.
    # Todo: Defaulting to NL for now.
    language = "NL"
    subject = _generate_subject(
        mail_type, product=product.translation.main_name, shop=shop_name, language=language, ticket_id=ticket_id
    )
    summary = generate_product_summary(ProductBase.from_orm(product), extra_content)

    contact_names = ", ".join([contact["name"] for contact in contacts])

    match mail_type:
        case MailType.INFO:
            body = _generate_mail_intro_for_product_info(contact_names, product, language, summary, nowtz())
        case _:
            raise ValueError(f"Unsupported target: {mail_type}")

    confirmation_mail: ConfirmationMail = {
        "message": body,
        "subject": subject,
        "to": contacts,
        "cc": [],
        "bcc": BCC,
        "language": language,
        "images": IMAGES_SHOP_VIRGE,
    }

    logger.info("Generated mail", language=language, subject=subject, target=mail_type)
    return confirmation_mail


@singledispatch
def generate_product_summary(model: ProductBase, extra_content: str | None = None) -> str:
    """Generate and return a HTML representation of a product summary.

    Specific implementations of this generic function will specify the model types they work on. For
    more info about the confirmation email templates please consult: :ref:`email-confirmation-templates`

    Args:
        product: Domain model for which to construct a payload.
        extra_content: Optional str to add extra text above the summary

    Returns:
    ---
        ProductTable summary in HTML

    Raises:
    --
        TypeError: in case a specific implementation could not be found. The domain model it was called for will be part of the error message.
        ValueError: in case error occurred whilst resource types couldn't be resolved in external systems.

    """
    return single_dispatch_base(generate_product_summary, model, extra_content)


@generate_product_summary.register
def shop_product_summary(product: ProductBase, extra_content: str | None = None) -> str:
    """Create and return an ConfirmationMail for :class:`~products.product_types.ntd.NtdProvisioning`.

    Args:
        model: NtdProvisioning
        extra_content: Optional str to add extra text above the summary
        kwargs: Extra arguments, only to be signature compatible

    Returns: HTML string
    """
    labels = {
        # section headers
        "title": product.translation.main_name,
        "product": "Product",
        # data fields
        "name": "Naam",
        "short_description": "Korte Beschrijving",
        "price": "Prijs",
        "category": "Categorie",
    }
    # Map domain model data to labels
    data = {
        "name": product.translation.main_name,
        "short_description": product.translation.main_description_short,
        "price": product.price,
        "category": product.category_id,
    }

    # Group data in to sections
    section_fields = {
        "product": ["name", "short_description", "price", "category"],
    }
    sections = ["product"]

    template = get_template_for_product_summary("product_summary.html.j2")
    return template.render(
        subscription=product.model_dump(),
        sections=sections,
        section_fields=section_fields,
        data=data,
        labels=labels,
        extra_content=extra_content,
    )


# @generate_product_summary.register
# def other_product_summary(subscription: OtherProvisioning, extra_content: str | None = None) -> str:
#     """Create and return an ConfirmationMail for :class:`~products.product_types.other.OtherProvisioning`.
#
#     Args:
#         model: OtherProvisioning
#         extra_content: Optional str to add extra text above the summary
#         kwargs: Extra arguments, only to be signature compatible
#
#     Returns: HTML string
#     """
#
#     # Todo BEV-3979: resolve the items from live system: contact and representative info should be
#     # resolved in the ET. That will enable us to re-send the confirmation mail at all times.
#
#     # Setup labels to translate fields
#     labels = {
#         # section headers
#         "title": "Titel",
#         "company": "Bedrijfsinformatie",
#         # data fields
#         "company_name": "Bedrijfsnaam",
#     }
#     # Map domain model data to labels
#     data = {
#         "company_name": subscription.other.company.chamber_of_commerce_name,
#     }
#
#     # Group data in to sections
#     section_fields = {
#         "company": ["company_name"],
#     }
#     sections = ["company"]
#
#     template = get_template_for_product_summary("other_summary.html.j2")
#     return template.render(
#         subscription=subscription.model_dump(),
#         sections=sections,
#         section_fields=section_fields,
#         data=data,
#         labels=labels,
#         extra_content=extra_content,
#     )

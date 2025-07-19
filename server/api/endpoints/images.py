import structlog
from fastapi import APIRouter

from server.api.helpers import create_presigned_url

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/signed-url/{image_name}")
def get_signed_url(image_name: str):
    image_url = create_presigned_url(image_name)
    return image_url

import structlog

from server.api.api_v1.router_fix import APIRouter
from server.api.helpers import create_presigned_url, delete_from_temporary_bucket, move_between_buckets

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/signed-url/{image_name}")
def get_signed_url(image_name: str):
    image_url = create_presigned_url(image_name)
    return image_url


@router.post("/move")
def move_images():
    return move_between_buckets()


@router.post("/delete-temp")
def delete_temporary_images():
    return delete_from_temporary_bucket()

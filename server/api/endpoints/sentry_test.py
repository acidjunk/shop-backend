from http import HTTPStatus
from fastapi import APIRouter
import structlog

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/", status_code=HTTPStatus.OK, response_model=None)
def trigger_error():
    logger.info("Manually triggering Sentry error")
    # Intentionally trigger an error
    1 / 0

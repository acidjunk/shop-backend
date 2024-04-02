from http import HTTPStatus
from typing import Any, List
from uuid import UUID

import structlog
from fastapi import HTTPException
from fastapi.param_functions import Body, Depends
from starlette.responses import Response

from server.api.api_v1.router_fix import APIRouter
from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.crud.crud_tag import tag_crud
from server.schemas.tag import TagCreate, TagSchema, TagUpdate

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[TagSchema])
def get_multi(response: Response, common: dict = Depends(common_parameters)) -> List[TagSchema]:
    tags, header_range = tag_crud.get_multi(
        skip=common["skip"], limit=common["limit"], filter_parameters=common["filter"], sort_parameters=common["sort"]
    )
    response.headers["Content-Range"] = header_range
    return tags


@router.get("/{id}", response_model=TagSchema)
def get_by_id(id: UUID) -> TagSchema:
    tag = tag_crud.get(id)
    if not tag:
        raise_status(HTTPStatus.NOT_FOUND, f"Tag with id {id} not found")
    return tag


@router.get("/name/{name}", response_model=TagSchema)
def get_by_name(name: str) -> TagSchema:
    tag = tag_crud.get_by_name(name=name)

    if not tag:
        raise_status(HTTPStatus.NOT_FOUND, f"Tag with name {name} not found")
    return tag


@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create(data: TagCreate = Body(...)) -> None:
    logger.info("Saving tag", data=data)
    tag = tag_crud.create(obj_in=data)
    return tag


@router.put("/{tag_id}", response_model=None, status_code=HTTPStatus.CREATED)
def update(*, tag_id: UUID, item_in: TagUpdate) -> Any:
    tag = tag_crud.get(id=tag_id)
    logger.info("Updating tag", data=tag)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    tag = tag_crud.update(
        db_obj=tag,
        obj_in=item_in,
    )
    return tag


@router.delete("/{tag_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(tag_id: UUID) -> None:
    try:
        tag_crud.delete(id=tag_id)
    except Exception as e:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail=f"{e.__cause__}")
    return

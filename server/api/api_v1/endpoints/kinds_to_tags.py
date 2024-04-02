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
from server.crud.crud_kind import kind_crud
from server.crud.crud_kind_to_tag import kind_to_tag_crud
from server.crud.crud_tag import tag_crud
from server.schemas.kind_to_tag import KindToTagCreate, KindToTagSchema, KindToTagUpdate

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[KindToTagSchema])
def get_multi(response: Response, common: dict = Depends(common_parameters)) -> List[KindToTagSchema]:
    """List prices for a kind_to_tag"""
    query_result, content_range = kind_to_tag_crud.get_multi(
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
    )
    response.headers["Content-Range"] = content_range
    return query_result


@router.get("/get_relation_id")
def get_relation_id(tag_id: UUID, kind_id: UUID) -> None:
    tag = tag_crud.get(tag_id)
    kind = kind_crud.get(kind_id)

    if not tag or not kind:
        raise_status(HTTPStatus.NOT_FOUND, "Tag or kind not found")

    relation = kind_to_tag_crud.get_relation_by_kind_tag(kind_id=kind.id, tag_id=tag.id)

    if not relation:
        raise_status(HTTPStatus.BAD_REQUEST, "Relation doesn't exist")

    return relation.id


@router.get("/{id}", response_model=KindToTagSchema)
def get_by_id(id: UUID) -> KindToTagSchema:
    kind_to_tag = kind_to_tag_crud.get(id)
    if not kind_to_tag:
        raise_status(HTTPStatus.NOT_FOUND, f"KindToTag with id {id} not found")
    return kind_to_tag


@router.post("/", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def create(data: KindToTagCreate = Body(...)) -> None:
    tag = tag_crud.get(data.tag_id)
    kind = kind_crud.get(data.kind_id)

    if not tag or not kind:
        raise_status(HTTPStatus.NOT_FOUND, "Tag or kind not found")

    logger.info("Saving kind_to_tag", data=data)
    return kind_to_tag_crud.create(obj_in=data)


@router.put("/{kind_to_tag_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def update(*, kind_to_tag_id: UUID, item_in: KindToTagUpdate) -> Any:
    kind_to_tag = kind_to_tag_crud.get(id=kind_to_tag_id)
    logger.info("Updating kind_to_tag", data=kind_to_tag)
    if not kind_to_tag:
        raise HTTPException(status_code=404, detail="Shop not found")

    kind_to_tag = kind_to_tag_crud.update(
        db_obj=kind_to_tag,
        obj_in=item_in,
    )
    return kind_to_tag


@router.delete("/{kind_to_tag_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(kind_to_tag_id: UUID) -> None:
    return kind_to_tag_crud.delete(id=kind_to_tag_id)

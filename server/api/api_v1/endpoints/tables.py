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
from server.crud.crud_table import table_crud
from server.schemas.table import TableCreate, TableSchema, TableUpdate

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[TableSchema])
def get_multi(response: Response, common: dict = Depends(common_parameters)) -> List[TableSchema]:
    tables, header_range = table_crud.get_multi(
        skip=common["skip"], limit=common["limit"], filter_parameters=common["filter"], sort_parameters=common["sort"]
    )
    response.headers["Content-Range"] = header_range
    return tables


@router.get("/{id}", response_model=TableSchema)
def get_by_id(id: UUID) -> TableSchema:
    table = table_crud.get(id)
    if not table:
        raise_status(HTTPStatus.NOT_FOUND, f"Table with id {id} not found")
    return table


@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create(data: TableCreate = Body(...)) -> None:
    logger.info("Saving table", data=data)
    table = table_crud.create(obj_in=data)
    return table


@router.put("/{table_id}", response_model=None, status_code=HTTPStatus.CREATED)
def update(*, table_id: UUID, item_in: TableUpdate) -> Any:
    table = table_crud.get(id=table_id)
    logger.info("Updating table", data=table)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    table = table_crud.update(
        db_obj=table,
        obj_in=item_in,
    )
    return table


@router.delete("/{table_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(table_id: UUID) -> None:
    return table_crud.delete(id=table_id)

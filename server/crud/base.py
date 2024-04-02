from typing import Any, Generic, List, Optional, Tuple, Type, TypeVar, Union

import structlog
from fastapi.encoders import jsonable_encoder
from more_itertools import one
from pydantic import BaseModel
from sqlalchemy import String, cast, or_
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm import Session
from sqlalchemy.sql import expression

from server.api.models import transform_json
from server.db import db
from server.db.database import BaseModel

logger = structlog.getLogger()

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class NotFound(Exception):
    pass


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, id: str) -> Optional[ModelType]:
        return db.session.query(self.model).get(id)

    def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filter_parameters: Optional[List[str]],
        sort_parameters: Optional[List[str]],
        query_parameter: Optional[Any] = None,
    ) -> Tuple[List[ModelType], str]:
        query = query_parameter
        if query is None:
            query = db.session.query(self.model)

        logger.debug(
            f"Filter and Sort parameters model={self.model}, sort_parameters={sort_parameters}, filter_parameters={filter_parameters}",
        )
        conditions = []

        if filter_parameters:
            for filter_parameter in filter_parameters:
                key, *value = filter_parameter.split(":", 1)

                # Use this branch if we detect a key value search (key:value) if it is just a single string (value)
                # treat the key as the value
                if len(value) > 0:
                    if key in sa_inspect(self.model).columns.keys():
                        conditions.append(cast(self.model.__dict__[key], String).ilike("%" + one(value) + "%"))
                    else:
                        logger.info(f"Key: not found in database model key={key}, model={self.model}")
                    query = query.filter(or_(*conditions))
                else:
                    if isinstance(value, list):
                        logger.info("Query parameters set to GET_MANY, ID column only", value=value)
                        conditions = []
                        for item in value:
                            conditions.append(self.model.__dict__["id"] == item)
                        query = query.filter(or_(*conditions))
                    else:
                        for column in sa_inspect(self.model).columns.keys():
                            conditions.append(cast(self.model.__dict__[column], String).ilike("%" + key + "%"))
                            query = query.filter(or_(*conditions))

        if sort_parameters and len(sort_parameters):
            for sort_parameter in sort_parameters:
                try:
                    sort_col, sort_order = sort_parameter.split(":")
                    if sort_col in sa_inspect(self.model).columns.keys():
                        if sort_order.upper() == "DESC":
                            query = query.order_by(expression.desc(self.model.__dict__[sort_col]))
                        else:
                            query = query.order_by(expression.asc(self.model.__dict__[sort_col]))
                    else:
                        logger.debug(f"Sort col does not exist sort_col={sort_col}")
                except ValueError:
                    if sort_parameter in sa_inspect(self.model).columns.keys():
                        query = query.order_by(expression.asc(self.model.__dict__[sort_parameter]))
                    else:
                        logger.debug(f"Sort param does not exist sort_parameter={sort_parameter}")

        # Generate Content Range Header Values
        count = query.count()

        if limit:
            # Limit is not 0: use limit
            response_range = "{}s {}-{}/{}".format(self.model.__name__.lower(), skip, skip + limit, count)
            return query.offset(skip).limit(limit).all(), response_range
        else:
            # Limit is 0: unlimited
            response_range = "{}s {}/{}".format(self.model.__name__.lower(), skip, count)
            return query.offset(skip).all(), response_range

    def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = transform_json(obj_in.dict())
        db_obj = self.model(**obj_in_data)
        db.session.add(db_obj)
        db.session.commit()
        db.session.refresh(db_obj)
        return db_obj

    def update(self, *, db_obj: ModelType, obj_in: UpdateSchemaType, commit: bool = True) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)

        # # Handle int based foreign key types:
        # for k, v in update_data.items():
        #     if isinstance(v, int):
        #         update_data[k] = v

        # Update DB record
        for field in obj_data:
            if field != "id" and field in update_data:
                setattr(db_obj, field, update_data[field])
        db.session.add(db_obj)

        # Set to false if you make two or more updates consecutively
        if commit:
            db.session.commit()

        return db_obj

    def delete(self, *, id: str) -> None:
        obj = db.session.query(self.model).get(id)
        if obj is None:
            raise NotFound
        db.session.delete(obj)
        db.session.commit()
        return None

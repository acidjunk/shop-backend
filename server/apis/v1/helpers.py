# Copyright 2024 René Dohmen <acidjunk@gmail.com>
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import base64
import os
from ast import literal_eval
from datetime import datetime
from http import HTTPStatus
from typing import Dict, List, Optional

# Add to requirments
# import boto3
import structlog
from sqlalchemy import String, cast, or_
from sqlalchemy.sql import expression

from server.api.error_handling import raise_status
from server.db import db

# s3 = boto3.resource(
#     "s3",
#     aws_access_key_id=os.getenv("IMAGE_S3_ACCESS_KEY_ID"),
#     aws_secret_access_key=os.getenv("IMAGE_S3_SECRET_ACCESS_KEY"),
# )
logger = structlog.get_logger(__name__)


def get_range_from_args(args):
    if args["range"]:
        range = []
        try:
            input = args["range"][1:-1].split(",")
            for i in input:
                range.append(int(i))
            logger.info("Query parameters set to custom range", range=range)
            return range
        except:  # noqa: E722
            logger.warning(
                "Query parameters not parsable",
                args=args.get(["range"], "No range provided"),
            )
    range = [0, 19]  # Default range
    logger.info("Query parameters set to default range", range=range)
    return range


def get_sort_from_args(args, default_sort="name", default_sort_order="ASC"):
    sort = []
    if args["sort"]:
        try:
            input = args["sort"].split(",")
            sort.append(input[0][2:-1])
            sort.append(input[1][1:-2])
            logger.info("Query parameters set to custom sort", sort=sort)
            return sort
        except:  # noqa: E722
            logger.warning(
                "Query parameters not parsable",
                args=args.get(["sort"], "No sort provided"),
            )
    sort = [default_sort, default_sort_order]  # Default sort
    logger.info("Query parameters set to default sort", sort=sort)
    return sort


def get_filter_from_args(args, default_filter={}):
    if args["filter"]:
        # print(args["filter"])
        try:
            filter = literal_eval(args["filter"].replace(":true", ":True").replace(":false", ":False"))
            logger.info("Query parameters set to custom filter", filter=filter)
            return filter
        except:  # noqa: E722
            logger.warning(
                "Query parameters not parsable",
                args=args.get(["filter"], "No filter provided"),
            )
    logger.info("Query parameters set to default filter", filter=default_filter)
    return default_filter


def save(item):
    try:
        db.session.add(item)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        raise_status(HTTPStatus.BAD_REQUEST, "DB error: {}".format(str(error)))


def load(model, id, fields=None, allow_404=False):
    if fields is None:
        fields = []

    if not fields:  # query "all" fields:
        item = model.query.filter_by(id=id).first()
    else:
        item = model.query.filter_by(id=id).first()
    if not item and not allow_404:
        raise_status(HTTPStatus.NOT_FOUND, f"Record id={id} not found")
    return item


def update(item, payload):
    if payload.get("id"):
        del payload["id"]
    try:
        for column, value in payload.items():
            setattr(item, column, value)
        save(item)
    except Exception as e:
        raise_status(HTTPStatus.INTERNAL_SERVER_ERROR, f"Error: {e}")
    return item


def delete(item):
    try:
        db.session.delete(item)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        raise_status(HTTPStatus.BAD_REQUEST, "DB error: {}".format(str(error)))


def query_with_filters(
    model,
    query,
    range: List[int] = None,
    sort: List[str] = None,
    filters: Optional[Dict] = None,
    quick_search_columns: List = ["name"],
):
    if filters != "":
        logger.info("filters dict", filters=filters)
        for column, searchPhrase in filters.items():
            if isinstance(searchPhrase, list):
                logger.info(
                    "Query parameters set to GET_MANY, ID column only",
                    column=column,
                    searchPhrase=searchPhrase,
                )
                conditions = []
                for item in searchPhrase:
                    conditions.append(model.__dict__["id"] == item)
                query = query.filter(or_(*conditions))
            elif searchPhrase is not None:
                logger.info(
                    "Query parameters set to custom filter for column",
                    column=column,
                    searchPhrase=searchPhrase,
                )
                if type(searchPhrase) == bool:
                    query = query.filter(model.__dict__[column].is_(searchPhrase))
                elif column.endswith("_gt"):
                    query = query.filter(model.__dict__[column[:-3]] > searchPhrase)
                elif column.endswith("_gte"):
                    query = query.filter(model.__dict__[column[:-4]] >= searchPhrase)
                elif column.endswith("_lte"):
                    query = query.filter(model.__dict__[column[:-4]] <= searchPhrase)
                elif column.endswith("_lt"):
                    query = query.filter(model.__dict__[column[:-3]] < searchPhrase)
                elif column.endswith("_ne"):
                    query = query.filter(model.__dict__[column[:-3]] != searchPhrase)
                elif column == "id":
                    query = query.filter_by(id=searchPhrase)
                elif column == "q":
                    logger.debug(
                        "Activating multi kolom filter",
                        column=column,
                        quick_search_columns=quick_search_columns,
                    )
                    conditions = []
                    for item in quick_search_columns:
                        conditions.append(cast(model.__dict__[item], String).ilike("%" + searchPhrase + "%"))
                    query = query.filter(or_(*conditions))
                else:
                    query = query.filter(cast(model.__dict__[column], String).ilike("%" + searchPhrase + "%"))

    if sort and len(sort) == 2:
        if sort[1].upper() == "DESC":
            query = query.order_by(expression.desc(model.__dict__[sort[0]]))
        else:
            query = query.order_by(expression.asc(model.__dict__[sort[0]]))

    range_start = int(range[0])
    range_end = int(range[1])
    if len(range) >= 2:
        total = query.count()
        # Range is inclusive so we need to add one
        range_length = max(range_end - range_start + 1, 0)
        query = query.offset(range_start)
        query = query.limit(range_length)
    else:
        total = query.count()

    content_range = f"items {range_start}-{range_end}/{total}"

    return query.all(), content_range


# def upload_file(blob, file_name):
#     image_mime, image_base64 = blob.split(",")
#     image = base64.b64decode(image_base64)
#
#     # Todo: make dynamic
#     s3_object = s3.Object("images-prijslijst-info", file_name)
#     resp = s3_object.put(Body=image, ContentType="image/png")
#
#     if resp["ResponseMetadata"]["HTTPStatusCode"] == 200:
#         logger.info("Uploaded file to S3", file_name=file_name)
#
#         # Make the result public
#         object_acl = s3_object.Acl()
#         response = object_acl.put(ACL="public-read")
#         logger.info("Made public", response=response)
#

# def name_file(column_name, record_name, image_name=""):
#     _, _, image_number = column_name.rpartition("_")[0:3]
#     current_name = image_name
#     extension = "png"  # todo: make it dynamic e.g. get it from mime-type, extra arg for this function?
#     if not current_name:
#         name = "".join([c if c.isalnum() else "-" for c in record_name])
#         name = f"{name}-{image_number}-1".lower()
#     else:
#         name, _ = current_name.split(".")
#         name, _, counter = name.rpartition("-")[0:3]
#         name = f"{name}-{int(counter) + 1}".lower()
#     name = f"{name}.{extension}"
#     logger.info("Named file", col_name=column_name, name_in=image_name, name_out=name)
#     return name


# def invalidateShopCache(shop_id):
#     item = load(Shop, shop_id)
#     item.modified_at = datetime.utcnow()
#     try:
#         save(item)
#     except Exception as e:
#         abort(500, f"Error: {e}")

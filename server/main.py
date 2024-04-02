#!/usr/bin/env python3

# Copyright 2019-2020 SURF.
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
import logging
import os

import structlog
from fastapi import Request
from fastapi.applications import FastAPI
from mangum import Mangum
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse

from server.api.api_v1.api import api_router
from server.api.error_handling import ProblemDetailException
from server.db import db
from server.db.database import DBSessionMiddleware
from server.exception_handlers.generic_exception_handlers import problem_detail_handler
from server.pydantic_forms.exception_handlers.fastapi import form_error_handler
from server.pydantic_forms.exceptions import FormException
from server.settings import app_settings
from server.version import GIT_COMMIT_HASH

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)

logger = structlog.get_logger(__name__)

app = FastAPI(
    title="Pricelist FastAPI",
    description="Backend for price-lists.",
    openapi_url="/v1/openapi.json",
    docs_url="/v1/docs",
    redoc_url="/v1/redoc",
    version=GIT_COMMIT_HASH,
    default_response_class=JSONResponse,
    # root_path="/backend",
    servers=[
        {"url": "/"},
    ],
)

app.include_router(api_router, prefix="/v1")

app.add_middleware(SessionMiddleware, secret_key=app_settings.SESSION_SECRET)
app.add_middleware(DBSessionMiddleware, database=db)
origins = app_settings.CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=app_settings.CORS_ALLOW_METHODS,
    allow_headers=app_settings.CORS_ALLOW_HEADERS,
    expose_headers=app_settings.CORS_EXPOSE_HEADERS,
)

app.add_exception_handler(FormException, form_error_handler)
app.add_exception_handler(ProblemDetailException, problem_detail_handler)


@app.router.get("/", response_model=str, response_class=JSONResponse, include_in_schema=False)
def index() -> str:
    return "FastAPI boilerplate backend root"


@app.router.get("/get_my_ip", include_in_schema=False)
def get_my_ip(request: Request):
    return {"ip": str(request.client.host), "alt": request.client}


logger.info("App is running")
handler = Mangum(app, lifespan="off")

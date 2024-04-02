import os
from typing import Dict, Optional

import requests
from dotenv import load_dotenv
from pydantic import BaseSettings, validator
from pydantic.networks import AnyHttpUrl

SUFFIX: str = "/v1/"


def acceptance_superuser_headers(uri: AnyHttpUrl) -> Dict[str, str]:
    login_data = {"username": os.environ.get("ACC_ADMIN_USER"), "password": os.environ.get("ACC_ADMIN_PASSWORD")}
    r = requests.post(uri + "login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


def production_superuser_headers(uri: AnyHttpUrl) -> Dict[str, str]:
    login_data = {"email": os.environ.get("PROD_ADMIN_USER"), "password": os.environ.get("PROD_ADMIN_PASSWORD")}
    r = requests.post(uri + "/login?next=/admin", data=login_data)
    token = r.request.headers._store["cookie"][1]
    headers = {"Cookie": f"{token}"}
    return headers


class AcceptanceSettings(BaseSettings):
    load_dotenv()
    BASE_ACC_BACKEND_URI: AnyHttpUrl = os.environ.get("BASE_ACC_BACKEND_URI") or "https://api.staging.prijslijst.info"
    ACC_BACKEND_URI = BASE_ACC_BACKEND_URI + SUFFIX
    BASE_PRD_BACKEND_URI: AnyHttpUrl = os.environ.get("BASE_PRD_BACKEND_URI") or "https://api.prijslijst.info"
    PRD_BACKEND_URI = BASE_PRD_BACKEND_URI + SUFFIX

    @validator("BASE_ACC_BACKEND_URI", pre=False)
    def validate_url(cls, v: str):
        if v.count("/") > 2:
            raise ValueError("please dont use suffixes")
        return v

    ACC_SUPERUSER_TOKEN_HEADERS = acceptance_superuser_headers(ACC_BACKEND_URI)
    PRD_SUPERUSER_TOKEN_HEADERS = production_superuser_headers(BASE_PRD_BACKEND_URI)


acceptance_settings = AcceptanceSettings()


if __name__ == "__main__":
    print(acceptance_settings.PRD_BACKEND_URI)
    print(acceptance_settings.ACC_BACKEND_URI)

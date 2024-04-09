#!/usr/bin/env python3

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
#
# -----------------------------------------------------------------------------
# USAGE/INSTRUCTIONS:
# -----------------------------------------------------------------------------
# This script can be used to query the current AWS Lambda Environment variables.
#
# You'll need a python with these packages to use the script:
# pydantic, pydantic, boto3, aws-sam-cli
#
# load your env stuff:
# $ python get-env.py staging


import os
import shutil
import sys

REGION_NAME = "eu-central-1"
ENV_PREFIX = "api-"
ENV_SUFFIX = "-prijslijst-info"
ENV_VARS = [
    "ENVIRONMENT",
    "TESTING",
    "DATABASE_URI",
    "SESSION_SECRET",
    "JWT_ALGORITHM",
    "IMAGE_S3_ACCESS_KEY_ID",
    "IMAGE_S3_SECRET_ACCESS_KEY",
    "LAMBDA_ACCESS_KEY_ID",
    "LAMBDA_SECRET_ACCESS_KEY",
    "FIRST_SUPERUSER",
    "FIRST_SUPERUSER_PASSWORD",
    "SMTP_HOST",
    "SMTP_USER",
    "SMTP_PASSWORD",
    "GUI_URI",
    "SMTP_ENABLED",
    "EMAILS_CC",
    "S3_BUCKET_IMAGES_ACCESS_KEY_ID",
    "S3_BUCKET_IMAGES_SECRET_ACCESS_KEY",
    "S3_BUCKET_IMAGES_NAME",
    "S3_BUCKET_TEMPORARY_NAME",
    "S3_TEMPORARY_ACCESS_KEY_ID",
    "S3_TEMPORARY_ACCESS_KEY",
    "S3_BUCKET_DOWNLOADS_NAME",
    "S3_BUCKET_DOWNLOADS_ACCESS_KEY_ID",
    "S3_BUCKET_DOWNLOADS_SECRET_ACCESS_KEY",
]


def check_aws_tooling():
    return shutil.which("aws") is not None


check_aws_tooling()
environment_name = sys.argv[1]
stack_name = f"{ENV_PREFIX}{environment_name}{ENV_SUFFIX}"
print(f"Derived stack name: {stack_name}")


cmd = f"aws lambda get-function-configuration --function-name {stack_name} " f"--region {REGION_NAME}"
print(f"CMD:\n{cmd}")
r = input("Continue? y/n: ")
if r == "y":
    os.system(cmd)

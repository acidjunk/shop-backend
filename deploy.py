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
# This script can be used to setup the needed AWS infra structure
# to run and deploy FastAPI to the Amazon Lamda gateway. You typically
# use it just once and after that you can use the deploy-staging.sh or
# deploy-production.sh script to update a running FastAPI instance with
# the latest version
#
# You'll need a python with these packages to use the script:
# pydantic, structlog, python-dotenv, sqlalchemy, pydantic, boto3, aws-sam-cli
#
#

import logging
import os
import shutil
import sys
from contextlib import closing

import boto3
import structlog
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from pydantic.networks import PostgresDsn
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url

REGION_NAME = "eu-central-1"
# Assuming: "staging" env =>
# api-staging-prijslijst-info
ENV_PREFIX = "api-"
ENV_SUFFIX = "-prijslijst-info"

DEPLOY_NEEDED = True


logger = structlog.get_logger(__name__)


def env_database_uri():
    if (env_var := os.environ.get("DATABASE_URI")) is not None:
        print("Skipping database creation: DATABASE_URI env variable provided.")
        return str(make_url(env_var)) or None


def db_uri(new_db_name):
    try:
        database_uri = PostgresDsn.build(
            scheme="postgresql",
            user=os.environ.get("POSTGRES_USER"),
            password=os.environ.get("POSTGRES_PASSWORD"),
            host=os.environ.get("POSTGRES_SERVER"),
            path=f"/{new_db_name or ''}",
        )
        url = make_url(database_uri)
        return url
    except TypeError as e:
        print("Try checking you env variables.")
        logging.error(e)


# NOTE: Needs a little change for SQLAlchemy 1.4
def create_db(new_db_name):
    url = db_uri(new_db_name)
    str_url = str(url)
    db_to_create = url.database
    url.database = "postgres"
    engine = create_engine(url)

    with closing(engine.connect()) as conn:
        conn.execute("COMMIT;")
        if conn.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_to_create}'").rowcount > 0:
            print("Skipping database creation: Database with this name already exists.")
        else:
            print(f"Database {db_to_create} created successfully.")
        # conn.execute("COMMIT;")
        # conn.execute(f'CREATE DATABASE "{db_to_create}";')
    return str_url


def create_bucket(s3_client, new_bucket_name, region):
    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).

    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """

    # Create bucket
    logger.info("creating new S3 bucket", bucket_name=new_bucket_name)
    try:
        if region is None:
            s3_client.create_bucket(Bucket=new_bucket_name)
        else:
            location = {"LocationConstraint": region}
            s3_client.create_bucket(Bucket=new_bucket_name, CreateBucketConfiguration=location)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def deploy(new_bucket_name, environment_name, db_conn_str):
    stack_name = f"{ENV_PREFIX}{environment_name}{ENV_SUFFIX}"
    logger.info("Determined stack_name", stack_name=stack_name)
    try:
        BASE_PATH = os.getcwd()
        # BUILD_DIR = "%s/%s" % (BASE_PATH, ".aws-sam/build")
        #
        # if not os.path.exists(BUILD_DIR):
        #     os.mkdir(BUILD_DIR)

        if DEPLOY_NEEDED:
            os.system(f"cd {BASE_PATH} && sam validate --template-file template-{environment_name}.yml")
            os.system(
                f"cd {BASE_PATH} && sam build --use-container --debug --template-file template-{environment_name}.yml"
            )
            os.system(
                f"cd {BASE_PATH} && sam package --s3-bucket {new_bucket_name} --template-file template-{environment_name}.yml --output-template-file out.yml --region {REGION_NAME}"
            )
            os.system(
                f"cd {BASE_PATH} && sam deploy --template-file out.yml --stack-name {stack_name} --region {REGION_NAME} --no-fail-on-empty-changeset "
                "--capabilities CAPABILITY_IAM"
            )
            os.system(
                f"cd {BASE_PATH} && aws lambda get-function-configuration --function-name {stack_name} --region {REGION_NAME}"
            )

        # Todo: extract to a separate function that can handle setting env vars
        envs = []
        envs.append(return_lambda_env_var(stack_name=stack_name, name="DATABASE_URI", value=db_conn_str))
        envs.append(
            return_lambda_env_var(
                stack_name=stack_name,
                name="SECRET_KEY",
                value=os.getenv("SECRET_KEY"),
            )
        )
        envs.append(
            return_lambda_env_var(
                stack_name=stack_name, name="SECURITY_PASSWORD_SALT", value=os.getenv("SECURITY_PASSWORD_SALT")
            )
        )
        cmd = (
            f"cd {os.getcwd()} && aws lambda update-function-configuration --function-name {stack_name} "
            f'--region {REGION_NAME} --environment "Variables={{{",".join(envs)}}}"'
        )
        os.system(cmd)

    except Exception as e:
        print(e)
        sys.exit(1)


def return_lambda_env_var(stack_name, name, value):
    logger.info("Gonna set Lambda env var", name=name, value=value, stack_name=stack_name)
    # cmd = (
    #     f"cd {os.getcwd()} && aws lambda update-function-configuration --function-name {stack_name} "
    #     f'--region {REGION_NAME} --environment "Variables={{{name}={value}}}"'
    # )
    return f"{name}={value}"


def check_environment_before_deploy():
    if (
        not os.getenv("AWS_ACCESS_KEY_ID")
        or not os.getenv("AWS_SECRET_ACCESS_KEY")
        or not os.getenv("SECURITY_PASSWORD_SALT")
        or not os.getenv("SECRET_KEY")
    ):
        logger.error("Please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, SECURITY_PASSWORD_SALT, SECRET_KEY env vars")
        sys.exit(1)


def check_aws_tooling():
    return shutil.which("aws") is not None


def main(environment_name):
    check_environment_before_deploy()
    client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=REGION_NAME,
    )

    create_new_s3_bucket = True
    new_bucket_name = f"{ENV_PREFIX}{environment_name}{ENV_SUFFIX}"
    existing_buckets = client.list_buckets()

    for bucket in existing_buckets["Buckets"]:
        if bucket["Name"] == new_bucket_name:
            create_new_s3_bucket = False
    if create_new_s3_bucket:
        create_bucket(client, new_bucket_name, REGION_NAME)
    else:
        logger.info("Skipping bucket creation as it already exists")

    db_conn_str = env_database_uri() or create_db(environment_name)
    logger.info("Using DB conn str for DB connection", db_uri=db_conn_str)
    answer = input("Are you sure you want to continue? y/n ")
    if answer == "y":
        deploy(new_bucket_name, environment_name, db_conn_str)


if __name__ == "__main__":
    load_dotenv()
    args = sys.argv

    if len(args) <= 1:
        logger.error("Please provide a full env name: e.g. PYTHONPATH=. python deploy.py staging")
        logger.info("NOTE: for now only 'staging' and 'production' are supported.")
        sys.exit()

    logger.info("Starting deployment for env", env=args[1])
    if not check_aws_tooling():
        logger.error("No AWS CLI found")
        sys.exit()
    main(environment_name=args[1])

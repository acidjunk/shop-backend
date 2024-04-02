# Pricelist backend

A backend for serving pricelists.

## Server

This project only works with Python 3.8, 3.9 and 3.10.
If you want to use a virtual environment first create the environment:

```bash
python3 -m venv .venv
source venv/bin/activate
```

You can install the required libraries with pip. The following command will install all the required
libraries for the project. Check out the different files under requirements to more specifically see
which library is used and for what reason.

```bash
pip install -r ./requirements/all.txt
```

A PostgreSQL user and two databases are required ('boilerplate' is the password used by default).

```bash
createuser -sP boilerplate
createdb boilerplate -O boilerplate
createdb boilerplate-test -O boilerplate
```

Now you should be able to start a hot reloading, api server:
```bash
PYTHONPATH=. uvicorn server.main:app --reload --port 8080
```

Or run a threaded server and auto-apply migrations on launch:
```bash
/bin/server
````

## Running tests
```bash
PYTHONPATH=. pytest tests/unit_tests
```

## Configuring the server

All configuration is done via ENV vars. 

```bash
export SESSION_SECRET="SUPER_DUPER_SECRET"
export TESTING=False
```

> Note: FastAPI will detect and automatically load an existing `.env` file. 

## DB Migrations

The database schema is maintained by migrations (see `/migrations` for the
definitions). Pending migrations are automatically applied when starting the
server.

There are 2 migration branches that move independently of one another. The data branch which contains
all needed data (e.g. examples etc.) and the Schema branch.

### Schema migration

Run this command prior to your first schema migration:

```bash
PYTHONPATH=. alembic upgrade heads
```

Then, to create a new schema migration:

```bash
PYTHONPATH=. alembic revision --autogenerate -m "New schema" --head=schema@head
```

This opens a new migration in `/migrations/versions/`

The initial scheme was created with:

```bash
PYTHONPATH=. alembic revision --autogenerate -m "Initial scheme" --head=schema@head --version-path=migrations/versions/schema
```

### General Migration

To create a data migration do the following:

```bash
PYTHONPATH=. alembic revision --message "Name of the migration" --head=general@head
```

This will also create a new revision file where normal SQL can be written like so:

```python
conn = op.get_bind()
res = conn.execute("INSERT INTO products VALUES ('x', 'y', 'z')")
```

## Manual deploy

Activate a python env with SAM installed, fire up Docker if it's not already running and run:

```
sam validate
sam build --use-container --debug
sam package --s3-bucket YOUR_S3_BUCKET \
--output-template-file out.yml --region eu-central-1
```

And then deploy it with:

```
sam deploy --template-file out.yml \
--stack-name fastapi-postgres-boilerplate \
--region eu-central-1 --no-fail-on-empty-changeset \
--capabilities CAPABILITY_IAM
```

A more detailed explanation about the deployment on Amazon lambda can be found on: 
[renedohmen.nl/deploy-fastapi-on-amazon-serverless](https://www.renedohmen.nl/deploy-fastapi-on-amazon-serverless/)

## Reset staging DB

use the RDS superuser to execute this on the staging DB

```
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
REASSIGN OWNED BY rds_super_user TO priceliststaging;
```

Now a prepared prod dump can be imported.

## Deployment problems

Deployment is still a bit rough and I set the needed ENV vars from a local script.

So after a deployment check if the login works in the swagger GUI. Sometimes the ENV var get reset and you have to 
run the `set-env.py` script for that environment. 

Currently, problems happened when:
- upgrading to a new python version via the SAM template
- when a build fails to deploy correctly (Noticed: when I added "-e requirement for pydantic-forms")

Running the `set-env.py` sets vars immediately without the need to restart something.


# Create a user

Set up the ENV var for FIRST_USER and run this command:

```bash
PYTHONPATH=. python server/create_initial_user.py
```

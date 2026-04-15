# Deployment

The canonical deployment instructions live in `README.md` — this page summarises them and points to the supporting files.

## Targets

- **AWS SAM** — see `template-production.yml` and `template-staging.yml`. Deploy via `deploy-production.sh` / `deploy-staging.sh`.
- **AWS App Runner** — see `apprunner.yaml`.

## SAM flow

```bash
sam validate
sam build --use-container --debug
sam package --s3-bucket YOUR_S3_BUCKET \
  --output-template-file out.yml --region eu-central-1

sam deploy --template-file out.yml \
  --stack-name fastapi-postgres-boilerplate \
  --region eu-central-1 --no-fail-on-empty-changeset \
  --capabilities CAPABILITY_IAM
```

See [the author's write-up](https://www.renedohmen.nl/deploy-fastapi-on-amazon-serverless/) for context on deploying FastAPI on Lambda.

## Environment variables

Production and staging ENV vars are set via `set-env.py` (wrapping AWS Parameter Store / Secrets Manager calls). The README notes that ENV vars sometimes reset during a deploy — re-run `set-env.py` in that case; it takes effect immediately without a service restart.

## Resetting staging

As the RDS superuser:

```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
REASSIGN OWNED BY rds_super_user TO priceliststaging;
```

Then import a fresh production dump.

## Docs site (Read the Docs)

The docs site is deployed separately via [Read the Docs](https://readthedocs.org) — not through SAM/App Runner. See [Contributing → Publishing the docs](../contributing.md#publishing-the-docs).

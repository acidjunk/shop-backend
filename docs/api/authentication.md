# Authentication

Authentication lives in `server/security.py` and is built on [AWS Cognito](https://aws.amazon.com/cognito/) via [`fastapi-cognito`](https://pypi.org/project/fastapi-cognito/).

## Token model

Two token shapes are accepted:

1. **User tokens** — standard Cognito-issued ID/access tokens for interactive users. Validated against the configured Cognito user pool and resolved to a `client_id` / subject.
2. **M2M (machine-to-machine) tokens** — Cognito client-credentials tokens. Must carry the `/api` scope. Used by server-to-server integrations.

The `CustomCognitoToken` model wraps the jose-decoded JWT and exposes the subject, scopes, and groups in a uniform shape.

- **Algorithm:** HS256 via [`python-jose`](https://pypi.org/project/python-jose/).
- **Password hashing** (for user records we store locally): bcrypt via `passlib[bcrypt]`.

## Configuration

All auth settings come from environment variables loaded by `server/settings.py`:

| Variable | Purpose |
|----------|---------|
| `AWS_COGNITO_USERPOOL_ID` | User pool the tokens are issued from. |
| `AWS_COGNITO_REGION` | AWS region of the user pool. |
| `AWS_COGNITO_CLIENT_ID` | Expected `aud` for user tokens. |
| `AWS_COGNITO_M2M_CLIENT_ID` | Expected `client_id` for M2M tokens. |
| `JWT_ALGORITHM` | Default `HS256`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Default `120`. |
| `SESSION_SECRET` | Signing key for `SessionMiddleware` cookies. |

Cognito itself — user pool, app clients, domain, groups — is managed outside this repo.

## Dependency usage

Protect an endpoint with the `auth_required()` dependency:

```python
from fastapi import Depends
from server.security import auth_required

@router.get("/protected")
def protected_route(token = Depends(auth_required)):
    ...
```

`auth_required` accepts both user and M2M tokens. For M2M-only endpoints, the handler can assert on `token.scopes` inside the body.

## Shop access checks

Authentication proves *who* is calling; authorisation proves *what shop* they can touch. Shop-scoped handlers resolve the caller's `UserTable` row and check `ShopUserTable` for a link to the `shop_id` path parameter. M2M tokens with `/api` scope bypass the per-shop check (they're trusted server credentials).

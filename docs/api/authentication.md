---
title: Authentication & Authorization
description: Cognito token handling, local JWT compatibility, and shop access checks.
---

# Authentication

Authentication lives in `server/security.py` and is built on [AWS Cognito](https://aws.amazon.com/cognito/) via [`fastapi-cognito`](https://pypi.org/project/fastapi-cognito/).

## Summary

- `auth_required` is the main dependency for Cognito-backed API access.
- Two token shapes are accepted: user tokens and M2M client-credentials tokens.
- A second, older local JWT system still exists for endpoints that authenticate against the local `UserTable`.
- Authentication and shop authorization are separate checks.

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

### Example: call a protected endpoint

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8080/shops/<shop-id>/products
```

If this returns **401**, check token validity and Cognito configuration. If it returns **403**, check the caller's role or shop access mapping.

## Legacy local JWT system

`server/api/deps.py` contains a second, older auth system using locally-signed JWTs (HS256, signed with `SESSION_SECRET`). It is used by endpoints that return a `UserTable` object rather than a `CognitoToken`:

- `get_current_user` — decodes the JWT, looks up the user in `UserTable` by `sub` (user ID).
- `get_current_active_user` — wraps the above, additionally checks `is_active`.
- `get_current_active_superuser` / `get_current_active_employee` — role checks on top.

Tokens for this system are issued by `POST /login/access-token` (username + password against the local `UserTable`). **Do not mix** these dependencies with `auth_required` — they return different types.

> **Passlib/bcrypt compatibility:** `passlib` crashes with `bcrypt >= 4.x` (`ValueError: password cannot be longer than 72 bytes`). Pin to `bcrypt==4.0.1` if you hit this locally.

## Shop access checks

Authentication proves *who* is calling; authorisation proves *what shop* they can touch. Shop-scoped handlers resolve the caller's `UserTable` row and check `ShopUserTable` for a link to the `shop_id` path parameter. M2M tokens with `/api` scope bypass the per-shop check (they're trusted server credentials).

## Troubleshooting

- **401 on every Cognito-protected route:** verify `AWS_COGNITO_USERPOOL_ID`, region, and client IDs in the environment. Placeholder defaults in `server/settings.py` will not work against real tokens.
- **Password login works but `auth_required` does not:** you are probably mixing the local JWT system with Cognito-backed dependencies. They return different token/user shapes.
- **403 on a shop route:** the user authenticated successfully, but there is no matching `ShopUserTable` association for the requested `shop_id`.

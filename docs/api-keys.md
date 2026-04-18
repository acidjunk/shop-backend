# API Keys

API keys allow programmatic access to protected endpoints as an alternative to Cognito JWT tokens.

## Endpoints

All management endpoints require a valid Cognito JWT.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api-keys/` | List your API keys (paginated) |
| `POST` | `/api-keys/` | Create a new API key |
| `DELETE` | `/api-keys/{id}` | Revoke an API key |

## Creating a Key

```http
POST /api-keys/
Authorization: Bearer <cognito-jwt>
```

Returns a JSON object that includes the raw `api_key` value. **This is the only time the raw key is returned** — store it securely.

## Using a Key

Pass the raw key in the `X-API-Key` header on any protected endpoint:

```http
GET /shops/{shop_id}/products/
X-API-Key: <your-api-key>
```

Endpoints that accept `auth_required()` support both API keys and Cognito JWTs. If `X-API-Key` is present it takes precedence.

## Revoking a Key

```http
DELETE /api-keys/{id}
Authorization: Bearer <cognito-jwt>
```

Returns `204 No Content`. Revocation is a soft delete — the record is kept for audit purposes but the key immediately stops working. You can only revoke your own keys.

## How Verification Works

When a request arrives with `X-API-Key`:

1. Compute SHA256 fingerprint of the provided key.
2. Look up the key record by fingerprint (indexed).
3. Check that `revoked_at` is null.
4. bcrypt-verify the raw key against the stored hash.

The raw key is never stored — only the bcrypt hash and the SHA256 fingerprint are persisted.

# Email notifications

Transactional email is rendered with Jinja2 and sent via SMTP.

## Implementation

- **Entry point:** `server/mail.py`.
- **Templates:** `server/mail_templates/{en,nl}/*.html.j2` — English and Dutch variants, each with a shared macros directory and image assets.
- **SMTP credentials:** `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAILS_FROM_EMAIL` (see `server/settings.py`).

## Order confirmation flow

When an order transitions to "completed" (commit `8dbfd02`), the order endpoint calls:

```python
send_order_confirmation_emails(order, shop, account)
```

This renders and sends two mails:

1. **Customer confirmation** — `mail_order_confirmation_customer.html.j2`.
2. **Shop-owner notification** — `mail_order_confirmation_owner.html.j2`.

```mermaid
sequenceDiagram
    autonumber
    participant EP as orders endpoint<br/>(complete order)
    participant Mail as mail.py
    participant J2 as Jinja2 env
    participant SMTP as SMTP server
    participant Cust as Customer inbox
    participant Own as Shop owner inbox

    EP->>Mail: send_order_confirmation_emails(order, shop, account)
    Mail->>J2: render customer template (lang = order.language)
    J2-->>Mail: HTML body
    Mail->>SMTP: SEND customer mail
    SMTP-->>Cust: delivered
    Mail->>J2: render owner template
    J2-->>Mail: HTML body
    Mail->>SMTP: SEND owner mail
    SMTP-->>Own: delivered
    Mail-->>EP: return (errors are logged, not raised)
```

The call site wraps the send in try/except and logs failures rather than aborting the request — a delivery error must not undo a successful order completion.

## Local smoke-testing (Mailpit)

A disabled-by-default endpoint lets you exercise the full render + SMTP path against a local Mailpit instance without creating a real order.

- **Setting:** `MAIL_TEST_ENDPOINT_ENABLED` (in `MailSettings`, default `False`).
- **Route:** `POST /mail-test/send-order-confirmation` (mounted only when the flag is true).
- **Payload:** `{ "to": "customer@example.com", "shop_name": "ShopVirge Dev", "owner_email": "owner@example.com" }` — all fields optional.

The endpoint builds synthetic shop/order/account objects in memory and calls `send_order_confirmation_emails`, so no database rows are created.

!!! warning
    Never enable `MAIL_TEST_ENDPOINT_ENABLED` in production. The route is unauthenticated; anyone who can reach the backend can trigger outbound mail.

## Language selection

Template language is picked per order based on the order's language field, falling back to English when absent or unknown. New locales are added by creating `server/mail_templates/<lang>/` with the same file layout as `en/`.

## Adding a new transactional email

1. Create `server/mail_templates/<lang>/mail_<name>.html.j2` for each supported language (reuse macros from `server/mail_templates/<lang>/macros/`).
2. Add a sender function in `server/mail.py` that renders the template and calls the shared SMTP helper.
3. Call it from the endpoint that triggers the side effect. Wrap in try/except so a delivery failure does not propagate.
4. Unit-test it by asserting the render output (don't hit a live SMTP server in tests — see `tests/unit_tests/test_mail.py` for the pattern: monkeypatch `server.mail.SMTP` and assert on `send_message` calls).

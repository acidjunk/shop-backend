# ShopVirge Backend

Welcome to the **ShopVirge Backend** documentation.

ShopVirge is a FastAPI REST API for managing shop pricelists, products, categories, orders, and attributes. It uses a multi-tenant architecture where most resources hang off a shop: `/shops/{shop_id}/...`.

!!! tip "FastAPI-style live API reference"
    The running server exposes an interactive OpenAPI UI at:

    - **Swagger UI:** `/docs`
    - **ReDoc:** `/redoc`
    - **Raw spec:** `/openapi.json`

    These are generated from the live FastAPI app, so they always match the running code. This site covers the architecture, rationale, and operational details that the OpenAPI spec can't.

## Where to go next

<div class="grid cards" markdown>

-   :material-rocket-launch: **[Quickstart](quickstart.md)**

    Get a local dev server running. Mirrors the content of `README.md`.

-   :material-graph: **[Architecture](architecture/overview.md)**

    Request flow, database layer, two-branch migrations, and C4 diagrams.

-   :material-api: **[API](api/overview.md)**

    Router layout, multi-tenant shop scoping, authentication, email notifications.

-   :material-code-tags-check: **[Development](development/setup.md)**

    Local setup, testing, code style, and writing migrations.

-   :material-cloud-upload: **[Deployment](deployment/overview.md)**

    AWS SAM + App Runner notes and the `set-env.py` workflow.

-   :material-source-pull: **[Contributing](contributing.md)**

    Branching, PR workflow, CI gates, and how the docs site is published.

</div>

## About this site

This site is built with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) — the same stack that powers the [FastAPI documentation](https://fastapi.tiangolo.com/). Diagrams are authored with [Mermaid](https://mermaid.js.org/) directly inside Markdown, and the existing drawio C4 diagrams are exported to SVG for the [C4 diagrams](architecture/diagrams.md) page.

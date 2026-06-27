"""Unit tests for CRUDApiKey — exercising CRUD-layer behaviour that HTTP tests can't reach."""

import pytest

from server.crud.crud_api_key import api_key_crud
from tests.unit_tests.factories.shop import make_shop


# ---------------------------------------------------------------------------
# lookup_by_plaintext — guard / short-circuit behaviour
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad_value",
    [
        "",
        "not-a-key",
        "Bearer sv_abc_def",  # auth header value passed by mistake
        "abc_prefix_body",    # missing sv_ prefix
    ],
)
def test_lookup_rejects_malformed_plaintext(bad_value):
    """lookup_by_plaintext returns None without hitting the DB for non-sv_ strings."""
    assert api_key_crud.lookup_by_plaintext(bad_value) is None


def test_lookup_returns_none_for_unknown_plaintext():
    """A well-formed sv_ string that was never minted returns None."""
    assert api_key_crud.lookup_by_plaintext("sv_xxxxxxxx_yyyyyyyyyyyyyyyyyyyyyyyyyyy") is None


def test_lookup_bumps_last_used_at():
    """Successful lookup stamps last_used_at; a second lookup sees it set."""
    shop_id = make_shop()
    row, plaintext = api_key_crud.mint(shop_id=shop_id, name="ts")

    assert row.last_used_at is None

    found = api_key_crud.lookup_by_plaintext(plaintext)
    assert found is not None
    assert found.last_used_at is not None


def test_lookup_returns_none_for_revoked_key():
    """lookup_by_plaintext returns None even when plaintext is correct but key is revoked."""
    shop_id = make_shop()
    row, plaintext = api_key_crud.mint(shop_id=shop_id, name="to-revoke")

    api_key_crud.revoke(shop_id=shop_id, key_id=row.id)

    assert api_key_crud.lookup_by_plaintext(plaintext) is None


# ---------------------------------------------------------------------------
# revoke — idempotency
# ---------------------------------------------------------------------------


def test_revoke_is_idempotent():
    """Revoking a key twice does not overwrite the first revoked_at timestamp."""
    shop_id = make_shop()
    row, _ = api_key_crud.mint(shop_id=shop_id, name="idem")

    first = api_key_crud.revoke(shop_id=shop_id, key_id=row.id)
    assert first is not None
    first_ts = first.revoked_at

    second = api_key_crud.revoke(shop_id=shop_id, key_id=row.id)
    assert second is not None
    assert second.revoked_at == first_ts


def test_revoke_unknown_key_returns_none():
    """revoke returns None for a key_id that doesn't belong to the shop."""
    from uuid import uuid4

    shop_id = make_shop()
    assert api_key_crud.revoke(shop_id=shop_id, key_id=uuid4()) is None


# ---------------------------------------------------------------------------
# list_by_shop — scoping and ordering
# ---------------------------------------------------------------------------


def test_list_by_shop_is_scoped():
    """Keys minted for shop A do not appear in list_by_shop for shop B."""
    shop_a = make_shop(random_shop_name=True)
    shop_b = make_shop(random_shop_name=True)

    api_key_crud.mint(shop_id=shop_a, name="key-a")

    assert api_key_crud.list_by_shop(shop_b) == []


def test_list_by_shop_returns_all_keys_for_shop():
    """list_by_shop returns every key minted for that shop."""
    shop_id = make_shop(random_shop_name=True)

    api_key_crud.mint(shop_id=shop_id, name="alpha")
    api_key_crud.mint(shop_id=shop_id, name="beta")
    api_key_crud.mint(shop_id=shop_id, name="gamma")

    keys = api_key_crud.list_by_shop(shop_id)
    assert len(keys) == 3
    assert {k.name for k in keys} == {"alpha", "beta", "gamma"}

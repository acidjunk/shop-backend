from http import HTTPStatus
from uuid import uuid4


def test_category_products_with_attributes(test_client, shop_with_category_attributes):
    """Returns products in a category with their attributes."""
    ids = shop_with_category_attributes
    response = test_client.get(f"/shops/{ids['shop_id']}/categories/{ids['cat1_id']}/products")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data) == 3  # 3 products in cat1

    # Each product should have attributes
    for item in data:
        assert len(item["attributes"]) > 0


def test_category_products_filter_by_option(test_client, shop_with_category_attributes):
    """Filter by option_id narrows results to matching products."""
    ids = shop_with_category_attributes
    response = test_client.get(
        f"/shops/{ids['shop_id']}/categories/{ids['cat1_id']}/products",
        params={"option_id": str(ids["size_s_id"])},
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    # prod1 and prod2 have size S in cat1
    assert len(data) == 2


def test_category_products_cat2(test_client, shop_with_category_attributes):
    """Category 2 has only 1 product with size M."""
    ids = shop_with_category_attributes
    response = test_client.get(f"/shops/{ids['shop_id']}/categories/{ids['cat2_id']}/products")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data) == 1
    assert len(data[0]["attributes"]) == 1  # only size M


def test_category_products_filter_no_match(test_client, shop_with_category_attributes):
    """Filter by option that doesn't exist in a category returns empty list."""
    ids = shop_with_category_attributes
    response = test_client.get(
        f"/shops/{ids['shop_id']}/categories/{ids['cat2_id']}/products",
        params={"option_id": str(ids["color_red_id"])},  # no color attributes in cat2
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


def test_category_products_nonexistent_category(test_client, shop_with_category_attributes):
    ids = shop_with_category_attributes
    fake_id = uuid4()
    response = test_client.get(f"/shops/{ids['shop_id']}/categories/{fake_id}/products")
    assert response.status_code == HTTPStatus.NOT_FOUND

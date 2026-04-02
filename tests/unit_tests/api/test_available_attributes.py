from http import HTTPStatus
from uuid import uuid4


def test_available_attributes_happy_path(test_client, shop_with_category_attributes):
    ids = shop_with_category_attributes
    response = test_client.get(f"/shops/{ids['shop_id']}/categories/{ids['cat1_id']}/available-attributes")
    assert response.status_code == HTTPStatus.OK

    data = response.json()
    assert len(data) == 2

    attrs_by_name = {a["name"]: a for a in data}

    # Verify size attribute
    size = attrs_by_name["size"]
    assert size["id"] == str(ids["size_attr_id"])
    assert size["unit"] == "EU"
    assert size["translation"]["main_name"] == "Maat"
    assert size["translation"]["alt1_name"] == "Size"
    assert size["translation"]["alt2_name"] == "Taille"

    size_opts = {o["value_key"]: o for o in size["options"]}
    assert len(size_opts) == 3
    # prod1 has S, prod2 has S => count 2
    assert size_opts["S"]["product_count"] == 2
    # prod2 has M => count 1
    assert size_opts["M"]["product_count"] == 1
    # prod3 has L => count 1
    assert size_opts["L"]["product_count"] == 1

    # Verify color attribute
    color = attrs_by_name["color"]
    assert color["id"] == str(ids["color_attr_id"])
    assert color["translation"]["main_name"] == "Kleur"
    assert color["translation"]["alt1_name"] == "Color"

    color_opts = {o["value_key"]: o for o in color["options"]}
    assert len(color_opts) == 2
    # prod1 and prod2 have RED => count 2
    assert color_opts["RED"]["product_count"] == 2
    # prod3 has BLUE => count 1
    assert color_opts["BLUE"]["product_count"] == 1


def test_available_attributes_category_scoping(test_client, shop_with_category_attributes):
    """Category 2 only has 1 product with size M — should only return size with M option."""
    ids = shop_with_category_attributes
    response = test_client.get(f"/shops/{ids['shop_id']}/categories/{ids['cat2_id']}/available-attributes")
    assert response.status_code == HTTPStatus.OK

    data = response.json()
    assert len(data) == 1

    attr = data[0]
    assert attr["name"] == "size"
    assert len(attr["options"]) == 1
    assert attr["options"][0]["value_key"] == "M"
    assert attr["options"][0]["product_count"] == 1


def test_available_attributes_empty_category(test_client, shop_with_category_attributes):
    """A category with no attribute values returns an empty list."""
    from tests.unit_tests.factories.categories import make_category

    ids = shop_with_category_attributes
    empty_cat_id = make_category(shop_id=ids["shop_id"], main_name="Empty", main_description="Empty category")

    response = test_client.get(f"/shops/{ids['shop_id']}/categories/{empty_cat_id}/available-attributes")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


def test_available_attributes_nonexistent_category(test_client, shop_with_category_attributes):
    ids = shop_with_category_attributes
    fake_id = uuid4()
    response = test_client.get(f"/shops/{ids['shop_id']}/categories/{fake_id}/available-attributes")
    assert response.status_code == HTTPStatus.NOT_FOUND

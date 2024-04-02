import uuid
from http import HTTPStatus

from server.utils.json import json_dumps


def test_shops_to_prices_get_multi(test_client, shop_with_products):
    response = test_client.get(f"/api/shops-to-prices")
    assert response.status_code == 200
    shops_to_prices = response.json()
    assert 3 == len(shops_to_prices)


def test_shop_to_price_get_by_id(test_client, shop_to_price_1):
    response = test_client.get(f"/api/shops-to-prices/{shop_to_price_1.id}")
    assert HTTPStatus.OK == response.status_code


def test_shop_to_price_get_by_id_not_found(test_client, shop_to_price_1):
    response = test_client.get(f"/api/shops-to-prices/{uuid.uuid4()}")
    assert HTTPStatus.NOT_FOUND == response.status_code


def test_shops_to_prices_create_with_nonexistent_product(
    test_client, price_3, shop_with_products, category_1, product_2, superuser_token_headers
):
    body = {
        "active": True,
        "new": False,
        "price_id": price_3.id,
        "shop_id": shop_with_products.id,
        "category_id": category_1.id,
        "product_id": product_2.id,
        "use_half": True,
        "use_one": True,
        "use_two_five": True,
        "use_five": True,
        "use_joint": True,
        "use_piece": True,
    }
    response = test_client.post(f"/api/shops-to-prices", data=json_dumps(body), headers=superuser_token_headers)
    assert response.status_code == HTTPStatus.CREATED


def test_shops_to_prices_create_with_existing_product(
    test_client, price_3, shop_with_products, category_1, product_1, superuser_token_headers
):
    body = {
        "active": True,
        "new": False,
        "price_id": price_3.id,
        "shop_id": shop_with_products.id,
        "category_id": category_1.id,
        "product_id": product_1.id,
        "use_half": True,
        "use_one": True,
        "use_two_five": True,
        "use_five": True,
        "use_joint": True,
        "use_piece": True,
    }
    response = test_client.post(f"/api/shops-to-prices", data=json_dumps(body), headers=superuser_token_headers)
    assert response.status_code == HTTPStatus.CONFLICT


def test_shops_to_prices_create_with_both_product_and_kind(
    test_client, price_3, shop_1, category_1, product_1, kind_1, superuser_token_headers
):
    body = {
        "active": True,
        "new": False,
        "price_id": price_3.id,
        "shop_id": shop_1.id,
        "category_id": category_1.id,
        "product_id": product_1.id,
        "kind_id": kind_1.id,
        "use_half": True,
        "use_one": True,
        "use_two_five": True,
        "use_five": True,
        "use_joint": True,
        "use_piece": True,
    }
    response = test_client.post(f"/api/shops-to-prices", data=json_dumps(body), headers=superuser_token_headers)
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_shops_to_prices_create_without_any_product_or_kind(
    test_client, price_3, shop_1, category_1, superuser_token_headers
):
    body = {
        "active": True,
        "new": False,
        "price_id": price_3.id,
        "shop_id": shop_1.id,
        "category_id": category_1.id,
        "use_half": True,
        "use_one": True,
        "use_two_five": True,
        "use_five": True,
        "use_joint": True,
        "use_piece": True,
    }
    response = test_client.post(f"/api/shops-to-prices", data=json_dumps(body), headers=superuser_token_headers)
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_shops_to_prices_create_shop_not_found(test_client, price_3, category_1, product_2, superuser_token_headers):
    body = {
        "active": True,
        "new": False,
        "price_id": price_3.id,
        "shop_id": str(uuid.uuid4()),
        "category_id": category_1.id,
        "product_id": product_2.id,
        "use_half": True,
        "use_one": True,
        "use_two_five": True,
        "use_five": True,
        "use_joint": True,
        "use_piece": True,
    }
    response = test_client.post(f"/api/shops-to-prices", data=json_dumps(body), headers=superuser_token_headers)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_shops_to_prices_update(test_client, shop_to_price_2, product_2, superuser_token_headers):
    shop_modified_at = test_client.get(
        f"/api/shops/cache-status/{shop_to_price_2.shop.id}", headers=superuser_token_headers
    ).json()["modified_at"]
    body = {
        "active": shop_to_price_2.active,
        "new": shop_to_price_2.new,
        "price_id": shop_to_price_2.price_id,
        "shop_id": shop_to_price_2.shop_id,
        "category_id": shop_to_price_2.category_id,
        "product_id": str(product_2.id),
        "use_half": shop_to_price_2.use_half,
        "use_one": shop_to_price_2.use_one,
        "use_two_five": shop_to_price_2.use_two_five,
        "use_five": shop_to_price_2.use_five,
        "use_joint": shop_to_price_2.use_joint,
        "use_piece": shop_to_price_2.use_piece,
    }
    response = test_client.put(
        f"/api/shops-to-prices/{shop_to_price_2.id}", data=json_dumps(body), headers=superuser_token_headers
    )
    assert response.status_code == HTTPStatus.CREATED

    updated_shop_to_price = test_client.get(
        f"/api/shops-to-prices/{shop_to_price_2.id}", headers=superuser_token_headers
    ).json()
    assert updated_shop_to_price["product_id"] == str(product_2.id)

    # Check if invalidateShopCache updates the modified_at
    shop_modified_at_new = test_client.get(
        f"/api/shops/cache-status/{shop_to_price_2.shop.id}", headers=superuser_token_headers
    ).json()["modified_at"]
    assert shop_modified_at_new > shop_modified_at


def test_shops_to_prices_delete(test_client, shop_to_price_1, superuser_token_headers):
    response = test_client.delete(f"/api/shops-to-prices/{shop_to_price_1.id}", headers=superuser_token_headers)
    assert HTTPStatus.NO_CONTENT == response.status_code
    shops_to_prices = test_client.get("/api/shops-to-prices").json()
    assert len(shops_to_prices) == 0


def test_shop_to_prices_swap(test_client, shop_with_products, superuser_token_headers):
    shop_to_price = shop_with_products.shops_to_price[1]

    response = test_client.patch(
        f"/api/shops-to-prices/swap/{shop_to_price.id}?move_up=true", headers=superuser_token_headers
    )
    assert response.status_code == 201

    response = test_client.get(f"/api/shops-to-prices/{shop_to_price.id}")
    shop_to_price_new = response.json()
    assert shop_to_price_new["order_number"] == 0


def test_shop_to_prices_swap_employee(test_client, shop_with_products, employee_token_headers):
    shop_to_price = shop_with_products.shops_to_price[1]

    response = test_client.patch(
        f"/api/shops-to-prices/swap/{shop_to_price.id}?move_up=true", headers=employee_token_headers
    )
    assert response.status_code == 201

    response = test_client.get(f"/api/shops-to-prices/{shop_to_price.id}")
    shop_to_price_new = response.json()
    assert shop_to_price_new["order_number"] == 0


def test_shop_to_prices_swap_wrong_employee(test_client, shop_with_products, employee_token_headers_2):
    shop_to_price = shop_with_products.shops_to_price[1]

    response = test_client.patch(
        f"/api/shops-to-prices/swap/{shop_to_price.id}?move_up=true", headers=employee_token_headers_2
    )
    assert response.status_code == 403


def test_shop_to_prices_swap_up_max(test_client, shop_with_products, superuser_token_headers):
    shop_to_price = shop_with_products.shops_to_price[0]

    response = test_client.patch(
        f"/api/shops-to-prices/swap/{shop_to_price.id}?move_up=true", headers=superuser_token_headers
    )
    assert response.status_code == 400


def test_shop_to_prices_swap_down_max(test_client, shop_with_products, superuser_token_headers):
    shop_to_price = shop_with_products.shops_to_price[2]

    response = test_client.patch(
        f"/api/shops-to-prices/swap/{shop_to_price.id}?move_up=false", headers=superuser_token_headers
    )
    assert response.status_code == 400

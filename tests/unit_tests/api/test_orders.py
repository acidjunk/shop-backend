# from server.api.endpoints.shop_endpoints.orders import get_price_rules_total
# from server.crud.crud_order import order_crud
# from server.schemas.order import OrderItem
#
#
# def test_order_list(test_client, shop_with_orders, superuser_token_headers):
#     response = test_client.get(f"/api/orders", headers=superuser_token_headers)
#     assert response.status_code == 200
#     assert len(response.json()) == 2
#
#
# def test_mixed_order_list(test_client, shop_with_mixed_orders, superuser_token_headers):
#     response = test_client.get(f"/api/orders", headers=superuser_token_headers)
#     assert response.status_code == 200
#     assert len(response.json()) == 2
#
#
# def test_orders_pending_list(test_client, shop_with_different_statuses_orders, shop_1, superuser_token_headers):
#     response = test_client.get(f"/api/orders/shop/{shop_1.id}/pending", headers=superuser_token_headers)
#     response_json = response.json()
#     assert response.status_code == 200
#     assert len(response_json) == 1
#     assert response_json[0]["status"] == "pending"
#
#
# def test_orders_complete_list(test_client, shop_with_different_statuses_orders, shop_1, superuser_token_headers):
#     response = test_client.get(f"/api/orders/shop/{shop_1.id}/complete", headers=superuser_token_headers)
#     response_json = response.json()
#     assert response.status_code == 200
#     assert len(response_json) == 2
#     assert response_json[0]["status"] == "complete"
#     assert response_json[1]["status"] == "cancelled"
#
#
# def test_create_order(test_client, price_1, price_2, kind_1, kind_2, shop_with_products):
#     items = [
#         {
#             "description": "1 gram",
#             "price": price_1.one,
#             "kind_id": str(kind_1.id),
#             "kind_name": kind_1.name,
#             "internal_product_id": "01",
#             "quantity": 2,
#         },
#         {
#             "description": "1 joint",
#             "price": price_2.joint,
#             "kind_id": str(kind_2.id),
#             "kind_name": kind_2.name,
#             "internal_product_id": "02",
#             "quantity": 1,
#         },
#     ]
#     body = {
#         "shop_id": str(shop_with_products.id),
#         "total": 24.0,  # 2x 1 gram of 10,- + 1 joint of 4
#         "order_info": items,
#     }
#     response = test_client.post(f"/api/orders", json=body)
#     assert response.status_code == 201, response.json()
#     response_json = response.json()
#     assert response_json["customer_order_id"] == 1
#     assert response_json["total"] == 24.0
#
#     order = order_crud.get_first_order_filtered_by(customer_order_id=1)
#     assert order.shop_id == shop_with_products.id
#     assert order.total == 24.0
#     assert order.customer_order_id == 1
#     assert order.status == "pending"
#     assert order.order_info == items
#
#     # test with a second order to also cover the automatic increase of `customer_order_id`
#     response = test_client.post(f"/api/orders", json=body)
#     response_json = response.json()
#     assert response_json["customer_order_id"] == 2
#     assert response_json["total"] == 24.0
#
#     assert response.status_code == 201
#     order = order_crud.get_first_order_filtered_by(customer_order_id=2)
#     assert order.customer_order_id == 2
#
#
# def test_create_mixed_order(test_client, price_1, price_2, price_3, product_1, kind_1, kind_2, shop_with_products):
#     items = [
#         {
#             "description": "1 gram",
#             "price": price_1.one,
#             "kind_id": str(kind_1.id),
#             "kind_name": kind_1.name,
#             "internal_product_id": "01",
#             "quantity": 2,
#         },
#         {
#             "description": "1 joint",
#             "price": price_2.joint,
#             "kind_id": str(kind_2.id),
#             "kind_name": kind_2.name,
#             "internal_product_id": "02",
#             "quantity": 1,
#         },
#         {
#             "description": "1",
#             "price": price_3.piece,
#             "product_id": str(product_1.id),
#             "product_name": product_1.name,
#             "internal_product_id": "03",
#             "quantity": 1,
#         },
#     ]
#     body = {
#         "shop_id": str(shop_with_products.id),
#         "total": 26.50,  # 2x 1 gram of 10,- + 1 joint of 4 + 1 cola (2.50)
#         "order_info": items,
#     }
#     response = test_client.post(f"/api/orders", json=body)
#     assert response.status_code == 201, response.json
#     response_json = response.json()
#     assert response_json["customer_order_id"] == 1
#     assert response_json["total"] == 26.50
#
#     order = order_crud.get_first_order_filtered_by(customer_order_id=1)
#     assert order.shop_id == shop_with_products.id
#     assert order.total == 26.50
#     assert order.customer_order_id == 1
#     assert order.status == "pending"
#     assert order.order_info == items
#
#     # test with a second order to also cover the automatic increase of `customer_order_id`
#     response = test_client.post(f"/api/orders", json=body)
#     response_json = response.json()
#     assert response_json["customer_order_id"] == 2
#     assert response_json["total"] == 26.50
#
#     assert response.status_code == 201, response.json
#     order = order_crud.get_first_order_filtered_by(customer_order_id=2)
#     assert order.customer_order_id == 2
#
#
# def test_create_order_validation(test_client, price_1, price_2, kind_1, kind_2, shop_with_products):
#     items = [
#         {
#             "description": "1 gram",
#             "price": price_1.one,
#             "kind_id": str(kind_1.id),
#             "kind_name": kind_1.name,
#             "internal_product_id": "01",
#             "quantity": 2,
#         },
#         {
#             "description": "1 joint",
#             "price": price_2.joint,
#             "kind_id": str(kind_2.id),
#             "kind_name": kind_2.name,
#             "internal_product_id": "02",
#             "quantity": 1,
#         },
#     ]
#     # Wrong shop_id
#     data = {
#         "shop_id": "afda6a2f-293d-4d76-a4f9-1a2d08b56835",
#         "total": 24.0,  # 2x 1 gram of 10,- + 1 joint of 4
#         "notes": "Nice one",
#         "order_info": items,
#     }
#     response = test_client.post(f"/api/orders", json=data)
#     assert response.status_code == 404
#
#     # No shop_id
#     data = {"total": 24.0, "notes": "Nice one", "order_info": items}  # 2x 1 gram of 10,- + 1 joint of 4
#     response = test_client.post(f"/api/orders", json=data)
#     assert response.status_code == 422
#
#     # Todo: test checksum functionality (totals should match with quantity in items)
#
#
# def test_price_rules():
#     order_info = [
#         OrderItem(
#             description="1 gram",
#             price=8,
#             kind_id="fd2f4ee4-a58e-425d-998b-003757b790eb",
#             kind_name="Soort 1",
#             product_id=None,
#             product_name=None,
#             internal_product_id="1",
#             quantity=1,
#         ),
#         OrderItem(
#             description="1 gram",
#             price=25,
#             kind_id="593277e5-f301-4662-9cf5-488e2479bac0",
#             kind_name="Soort 2",
#             product_id=None,
#             product_name=None,
#             internal_product_id="47",
#             quantity=1,
#         ),
#         OrderItem(
#             description="1 gram",
#             price=9,
#             kind_id="b13e26c3-834b-493f-a1d0-17859c41cea0",
#             kind_name="Soort 3",
#             product_id=None,
#             product_name=None,
#             internal_product_id="4",
#             quantity=1,
#         ),
#     ]
#
#     assert get_price_rules_total(order_info) == 3
#
#     # Check on quantity
#     order_info = [
#         OrderItem(
#             description="1 gram",
#             price=8,
#             kind_id="fd2f4ee4-a58e-425d-998b-003757b790eb",
#             kind_name="Soort 1",
#             product_id=None,
#             product_name=None,
#             internal_product_id="1",
#             quantity=4,
#         ),
#         OrderItem(
#             description="1 gram",
#             price=25,
#             kind_id="593277e5-f301-4662-9cf5-488e2479bac0",
#             kind_name="Soort 2",
#             product_id=None,
#             product_name=None,
#             internal_product_id="47",
#             quantity=1,
#         ),
#         OrderItem(
#             description="1 gram",
#             price=9,
#             kind_id="b13e26c3-834b-493f-a1d0-17859c41cea0",
#             kind_name="Soort 3",
#             product_id=None,
#             product_name=None,
#             internal_product_id="4",
#             quantity=1,
#         ),
#     ]
#     assert get_price_rules_total(order_info) == 6
#
#     # Check with 5g
#     order_info = [
#         OrderItem(
#             description="5 gram",
#             price=8,
#             kind_id="fd2f4ee4-a58e-425d-998b-003757b790eb",
#             kind_name="Soort 1",
#             product_id=None,
#             product_name=None,
#             internal_product_id="1",
#             quantity=1,
#         ),
#         OrderItem(
#             description="1 gram",
#             price=25,
#             kind_id="593277e5-f301-4662-9cf5-488e2479bac0",
#             kind_name="Soort 2",
#             product_id=None,
#             product_name=None,
#             internal_product_id="47",
#             quantity=1,
#         ),
#         OrderItem(
#             description="1 gram",
#             price=9,
#             kind_id="b13e26c3-834b-493f-a1d0-17859c41cea0",
#             kind_name="Soort 3",
#             product_id=None,
#             product_name=None,
#             internal_product_id="4",
#             quantity=1,
#         ),
#     ]
#     assert get_price_rules_total(order_info) == 7
#
#     # Check with joint
#     order_info = [
#         OrderItem(
#             description="1 gram",
#             price=8,
#             kind_id="fd2f4ee4-a58e-425d-998b-003757b790eb",
#             kind_name="Soort 1",
#             product_id=None,
#             product_name=None,
#             internal_product_id="1",
#             quantity=4,
#         ),
#         OrderItem(
#             description="1 gram",
#             price=25,
#             kind_id="593277e5-f301-4662-9cf5-488e2479bac0",
#             kind_name="Soort 2",
#             product_id=None,
#             product_name=None,
#             internal_product_id="47",
#             quantity=1,
#         ),
#         OrderItem(
#             description="joint",
#             price=6,
#             kind_id="a99f677f-14dc-4d67-9d41-ff3e85dd09fc",
#             kind_name="Mega Joint",
#             product_id=None,
#             product_name=None,
#             internal_product_id="26",
#             quantity=1,
#         ),
#     ]
#     assert get_price_rules_total(order_info) == 5.4
#
#
# def test_create_order_with_ip_allowed(test_client, price_1, kind_1, shop_with_testclient_ip_with_products):
#     items = [
#         {
#             "description": "1 gram",
#             "price": price_1.one,
#             "kind_id": str(kind_1.id),
#             "kind_name": kind_1.name,
#             "internal_product_id": "01",
#             "quantity": 2,
#         }
#     ]
#     body = {
#         "shop_id": str(shop_with_testclient_ip_with_products.id),
#         "total": 10.0,
#         "order_info": items,
#     }
#     response = test_client.post(f"/api/orders", json=body)
#     assert response.status_code == 201, response.json()
#     response_json = response.json()
#     assert response_json["customer_order_id"] == 1
#     assert response_json["total"] == 10.0
#
#     order = order_crud.get_first_order_filtered_by(customer_order_id=1)
#     assert order.shop_id == shop_with_testclient_ip_with_products.id
#     assert order.total == 10.0
#     assert order.customer_order_id == 1
#     assert order.status == "pending"
#     assert order.order_info == items
#
#
# def test_create_order_with_ip_not_allowed(test_client, price_1, kind_1, shop_with_custom_ip_with_products):
#     items = [
#         {
#             "description": "1 gram",
#             "price": price_1.one,
#             "kind_id": str(kind_1.id),
#             "kind_name": kind_1.name,
#             "internal_product_id": "01",
#             "quantity": 2,
#         }
#     ]
#     body = {
#         "shop_id": str(shop_with_custom_ip_with_products.id),
#         "total": 10.0,
#         "order_info": items,
#     }
#     response = test_client.post(f"/api/orders", json=body)
#     assert response.status_code == 400, response.json()
#     response_json = response.json()
#     assert response_json["detail"] == "NOT_ON_SHOP_WIFI"
#
#
# def test_patch_order_to_complete(test_client, shop_with_orders, superuser_token_headers):
#     # Get the uncompleted order_id from the fixture:
#     order = order_crud.get_first_order_filtered_by(status="pending")
#
#     body = {
#         "status": "complete",
#     }
#     response = test_client.patch(f"/api/orders/{order.id}", json=body, headers=superuser_token_headers)
#     assert response.status_code == 201
#
#     updated_order = test_client.get(f"/api/orders/{order.id}", headers=superuser_token_headers).json()
#     assert updated_order["status"] == "complete"
#     assert updated_order["completed_at"] is not None
#
#
# def test_update_order(test_client, shop_with_orders, superuser_token_headers):
#     # Get the completed order_id from the fixture:
#     order = order_crud.get_first_order_filtered_by(status="complete")
#
#     body = {"status": "cancelled", "order_info": order.order_info, "shop_id": str(order.shop_id)}
#     response = test_client.put(f"/api/orders/{order.id}", json=body, headers=superuser_token_headers)
#     assert response.status_code == 201
#
#     updated_order = test_client.get(f"/api/orders/{order.id}", headers=superuser_token_headers).json()
#     assert updated_order["status"] == "cancelled"
#
#
# def test_delete_order(test_client, shop_with_orders, superuser_token_headers):
#     order = order_crud.get_first_order_filtered_by(status="complete")
#
#     response = test_client.delete(f"/api/orders/{order.id}", headers=superuser_token_headers)
#     assert response.status_code == 204
#
#     orders = test_client.get("/api/orders", headers=superuser_token_headers).json()
#     assert 1 == len(orders)

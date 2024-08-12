# from server.utils.json import json_dumps
#
#
# def test_shops_users_get_users_by_shop(test_client, superuser_token_headers, user_admin, user_employee, shop_1):
#     response = test_client.get(f"/api/shops-users/shop/{shop_1.id}", headers=superuser_token_headers)
#     assert response.status_code == 200
#
#     shops_users = response.json()
#     shops_users_ids = [shop_user["user_id"] for shop_user in shops_users]
#
#     assert shops_users_ids.__contains__(str(user_employee.id))
#     assert shops_users_ids.__contains__(str(user_admin.id))
#     assert 2 == len(shops_users)
#
#
# def test_shops_users_get_shops_by_user(test_client, superuser_token_headers, user_admin, shop_1, shop_2):
#     response = test_client.get(f"/api/shops-users/user/{user_admin.id}", headers=superuser_token_headers)
#     assert response.status_code == 200
#
#     shops_users = response.json()
#     shops_users_ids = [shop_user["shop_id"] for shop_user in shops_users]
#
#     assert shops_users_ids.__contains__(str(shop_1.id))
#     assert shops_users_ids.__contains__(str(shop_2.id))
#     assert 2 == len(shops_users)
#
#
# def test_assign_shop_to_user(test_client, superuser_token_headers, user_employee, shop_2):
#     body = {"user_id": str(user_employee.id), "shop_id": str(shop_2.id)}
#
#     response = test_client.post(f"/api/shops-users/", data=json_dumps(body), headers=superuser_token_headers)
#     assert response.status_code == 201
#
#     response = test_client.get(f"/api/shops-users/user/{user_employee.id}", headers=superuser_token_headers)
#     assert response.status_code == 200
#
#     shops_users = response.json()
#     shops_users_ids = [shop_user["shop_id"] for shop_user in shops_users]
#     assert shops_users_ids.__contains__(str(shop_2.id))
#
#
# def test_delete(test_client, superuser_token_headers, user_admin):
#     response = test_client.get(f"/api/shops-users/user/{user_admin.id}", headers=superuser_token_headers)
#     shops_user_relation_id = response.json()[0]["id"]
#
#     response = test_client.delete(f"/api/shops-users/{shops_user_relation_id}", headers=superuser_token_headers)
#     assert response.status_code == 200
#
#     response = test_client.get(f"/api/shops-users/user/{user_admin.id}", headers=superuser_token_headers)
#     assert response.status_code == 200
#
#     shops_users = response.json()
#     assert 1 == len(shops_users)

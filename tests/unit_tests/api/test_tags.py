# from http import HTTPStatus
# from uuid import uuid4
#
# import structlog
#
# from server.utils.json import json_dumps
#
# logger = structlog.getLogger(__name__)
#
#
# def test_tags_get_multi(tag_1, test_client, superuser_token_headers):
#     response = test_client.get("/api/tags", headers=superuser_token_headers)
#
#     assert HTTPStatus.OK == response.status_code
#     tags = response.json()
#
#     assert 15 == len(tags)
#
#
# def test_tag_get_by_id(tag_2, test_client, superuser_token_headers):
#     response = test_client.get(f"/api/tags/{tag_2.id}", headers=superuser_token_headers)
#     print(response.__dict__)
#     assert HTTPStatus.OK == response.status_code
#     tag = response.json()
#     assert tag["name"] == "FocusedTest"
#
#
# def test_tag_get_by_id_404(tag_1, test_client, superuser_token_headers):
#     response = test_client.get(f"/api/tags/{str(uuid4())}", headers=superuser_token_headers)
#     assert HTTPStatus.NOT_FOUND == response.status_code
#
#
# def test_tag_save(test_client, superuser_token_headers):
#     body = {"name": "New Tag"}
#
#     response = test_client.post("/api/tags/", data=json_dumps(body), headers=superuser_token_headers)
#     assert HTTPStatus.CREATED == response.status_code
#     tags = test_client.get("/api/tags", headers=superuser_token_headers).json()
#     assert 15 == len(tags)
#
#
# def test_tag_update(tag_1, test_client, superuser_token_headers):
#     body = {"name": "Updated Tag"}
#     response = test_client.put(f"/api/tags/{tag_1.id}", data=json_dumps(body), headers=superuser_token_headers)
#     assert HTTPStatus.CREATED == response.status_code
#
#     response_updated = test_client.get(f"/api/tags/{tag_1.id}", headers=superuser_token_headers)
#     tag = response_updated.json()
#     assert tag["name"] == "Updated Tag"
#
#
# def test_tag_delete(tag_1, test_client, superuser_token_headers):
#     response = test_client.delete(f"/api/tags/{tag_1.id}", headers=superuser_token_headers)
#     assert HTTPStatus.NO_CONTENT == response.status_code
#     shops = test_client.get("/api/tags", headers=superuser_token_headers).json()
#     assert 14 == len(shops)

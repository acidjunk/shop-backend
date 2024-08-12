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
# def test_strains_get_multi(strain_1, strain_2, test_client, superuser_token_headers):
#     response = test_client.get("/api/strains", headers=superuser_token_headers)
#
#     assert HTTPStatus.OK == response.status_code
#     strains = response.json()
#
#     assert 2 == len(strains)
#
#
# def test_strain_get_by_id(strain_1, test_client, superuser_token_headers):
#     response = test_client.get(f"/api/strains/{strain_1.id}", headers=superuser_token_headers)
#     print(response.__dict__)
#     assert HTTPStatus.OK == response.status_code
#     strain = response.json()
#     assert strain["name"] == "Haze"
#
#
# def test_strain_get_by_id_404(strain_1, test_client, superuser_token_headers):
#     response = test_client.get(f"/api/strains/{str(uuid4())}", headers=superuser_token_headers)
#     assert HTTPStatus.NOT_FOUND == response.status_code
#
#
# def test_strain_save(test_client, superuser_token_headers):
#     body = {"name": "New Strain"}
#
#     response = test_client.post("/api/strains/", data=json_dumps(body), headers=superuser_token_headers)
#     assert HTTPStatus.CREATED == response.status_code
#     strains = test_client.get("/api/strains", headers=superuser_token_headers).json()
#     assert 1 == len(strains)
#
#
# def test_strain_update(strain_1, test_client, superuser_token_headers):
#     body = {"name": "Updated Strain"}
#     response = test_client.put(f"/api/strains/{strain_1.id}", data=json_dumps(body), headers=superuser_token_headers)
#     assert HTTPStatus.CREATED == response.status_code
#
#     response_updated = test_client.get(f"/api/strains/{strain_1.id}", headers=superuser_token_headers)
#     strain = response_updated.json()
#     assert strain["name"] == "Updated Strain"
#
#
# def test_strain_delete(strain_1, test_client, superuser_token_headers):
#     response = test_client.delete(f"/api/strains/{strain_1.id}", headers=superuser_token_headers)
#     assert HTTPStatus.NO_CONTENT == response.status_code
#     strains = test_client.get("/api/strains", headers=superuser_token_headers).json()
#     assert 0 == len(strains)

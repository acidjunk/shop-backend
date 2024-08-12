# from http import HTTPStatus
# from unittest import TestCase
#
# import pytest
#
# from server.api.error_handling import ProblemDetailException
# from server.api.models import validate
# from server.db import Shop
#
#
# class TestModels(TestCase):
#     def test_validate(self):
#         with pytest.raises(ProblemDetailException) as excinfo:
#             validate(Shop, {})
#
#         assert excinfo.value.status_code == HTTPStatus.BAD_REQUEST
#         assert excinfo.value.detail == "Missing attributes 'name' for Shop"

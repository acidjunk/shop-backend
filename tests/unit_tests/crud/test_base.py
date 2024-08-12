# import pytest
#
# from server import crud
# from server.crud.crud_strain import strain_crud
#
#
# @pytest.mark.xfail(reason="blaat")
# def test_filter(strain_1, strain_2):
#     result, content_range = strain_crud.get_multi(filter_parameters=["name:Haze"], sort_parameters=[])
#     assert len(result) == 1
#     assert content_range == "strains 0-100/1"
#
#     # Will not filter but return all results
#     result, content_range = strain_crud.get_multi(filter_parameters=["NONEXISITANT:0"], sort_parameters=[])
#     assert len(result) == 2
#     assert content_range == "strains 0-100/2"
#
#     # Wild card match on all tables
#     result, content_range = strain_crud.get_multi(filter_parameters=["Haze"], sort_parameters=[])
#     assert len(result) == 1
#     assert content_range == "strains 0-100/1"
#
#
# def test_sort(strain_1, strain_2):
#     result, content_range = strain_crud.get_multi(filter_parameters=[], sort_parameters=["name:ASC"])
#     assert len(result) == 2
#     assert content_range == "strains 0-100/2"
#
#     assert result[0].name == "Haze"
#
#     result, content_range = strain_crud.get_multi(filter_parameters=[], sort_parameters=["name:DESC"])
#     assert len(result) == 2
#     assert content_range == "strains 0-100/2"
#
#     assert result[0].name == "Kush"
#
#     # No Sort order
#     result, content_range = strain_crud.get_multi(filter_parameters=[], sort_parameters=["name"])
#     assert len(result) == 2
#     assert content_range == "strains 0-100/2"
#
#     assert result[0].name == "Haze"
#
#     # Non existant column impossible to sort
#     result, content_range = strain_crud.get_multi(filter_parameters=[], sort_parameters=["NONTRUE"])
#     assert len(result) == 2
#     assert content_range == "strains 0-100/2"
#
#     # Non existant column impossible to sort on nonexistant method
#     result, content_range = strain_crud.get_multi(filter_parameters=[], sort_parameters=["NONTRUE:NONTRUE"])
#     assert len(result) == 2
#     assert content_range == "strains 0-100/2"

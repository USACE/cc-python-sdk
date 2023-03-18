import pytest
import json

from attr.exceptions import FrozenInstanceError
from cc_sdk import DataSource


@pytest.fixture
def data_source():
    return DataSource(
        name="test", id="123", store_name="test_store", paths=["path1", "path2"]
    )


def test_value_error():
    with pytest.raises(ValueError):
        _ = DataSource(
            name="test", id="123", store_name="test_store", paths=["path1", object()]
        )


def test_getters(data_source):
    assert data_source.name == "test"
    assert data_source.id == "123"
    assert data_source.store_name == "test_store"
    assert data_source.paths == ["path1", "path2"]


def test_setters(data_source):
    with pytest.raises(FrozenInstanceError):
        data_source.name = "new_test"

    with pytest.raises(FrozenInstanceError):
        data_source.id = "456"

    with pytest.raises(FrozenInstanceError):
        data_source.store_name = "new_test_store"

    with pytest.raises(FrozenInstanceError):
        data_source.paths = ["new_path"]


def test_serialize(data_source):
    expected_json = '{"name": "test", "id": "123", "store_name": "test_store", "paths": ["path1", "path2"]}'
    assert data_source.serialize() == expected_json
    assert json.loads(data_source.serialize()) == json.loads(expected_json)

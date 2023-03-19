import json
import pytest
from cc_sdk import DataStore, StoreType

# pylint: disable=redefined-outer-name


@pytest.fixture
def data_store():
    return DataStore(
        name="test",
        id="123",
        parameters={"param1": "value1", "param2": "value2"},
        store_type=StoreType.S3,
        ds_profile="test_profile",
    )


def test_getters(data_store):
    assert data_store.name == "test"
    assert data_store.id == "123"
    assert data_store.parameters == {"param1": "value1", "param2": "value2"}
    assert data_store.store_type == StoreType.S3
    assert data_store.ds_profile == "test_profile"
    assert data_store.session is None


def test_setters(data_store):
    with pytest.raises(AttributeError):
        data_store.name = "new_test"

    with pytest.raises(AttributeError):
        data_store.id = "456"

    with pytest.raises(AttributeError):
        data_store.parameters = {"new_param1": "new_value1"}

    with pytest.raises(AttributeError):
        data_store.store_type = StoreType.EBS

    with pytest.raises(AttributeError):
        data_store.ds_profile = "new_test_profile"


def test_serialize(data_store):
    expected_json = '{"name": "test", "id": "123", "parameters": {"param1": "value1", "param2": "value2"}, \
        "store_type": "S3", "ds_profile": "test_profile"}'
    assert data_store.serialize() == json.dumps(json.loads(expected_json))
    assert json.loads(data_store.serialize()) == json.loads(expected_json)

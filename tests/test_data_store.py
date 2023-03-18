import pytest
from cc_sdk import DataStore, StoreType
import json


@pytest.fixture
def data_store():
    return DataStore(
        name="test",
        id="123",
        parameters={"param1": "value1", "param2": "value2"},
        store_type=StoreType.S3,
        ds_profile="test_profile",
    )


def test_type_errors():
    with pytest.raises(TypeError):
        _ = DataStore(
            name=object(),
            id="123",
            parameters={"param1": "value1", "param2": "value2"},
            store_type=StoreType.S3,
            ds_profile="test_profile",
        )
    with pytest.raises(TypeError):
        _ = DataStore(
            name="test",
            id=object(),
            parameters={"param1": "value1", "param2": "value2"},
            store_type=StoreType.S3,
            ds_profile="test_profile",
        )
    with pytest.raises(TypeError):
        _ = DataStore(
            name="test",
            id="123",
            parameters=object(),
            store_type=StoreType.S3,
            ds_profile="test_profile",
        )
    with pytest.raises(TypeError):
        _ = DataStore(
            name="test",
            id="123",
            parameters={"param1": "value1", "param2": "value2"},
            store_type=object(),
            ds_profile="test_profile",
        )
    with pytest.raises(TypeError):
        _ = DataStore(
            name="test",
            id="123",
            parameters={"param1": "value1", "param2": "value2"},
            store_type=StoreType.S3,
            ds_profile=object(),
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

    with pytest.raises(ValueError):
        data_store.session = object()  # non-serializable object

    data_store.session = {"key": "value"}  # serializable object
    assert data_store.session == {"key": "value"}


def test_serialize(data_store):
    # Serialize the DataStore object
    serialized = data_store.serialize()

    # Deserialize the JSON string back into a dictionary
    deserialized = json.loads(serialized)

    # Check that the dictionary has the same attribute values as the original DataStore object
    assert deserialized["name"] == data_store.name
    assert deserialized["id"] == data_store.id
    assert deserialized["parameters"] == data_store.parameters
    assert deserialized["store_type"] == "S3"
    assert deserialized["ds_profile"] == data_store.ds_profile
    assert deserialized["session"] == data_store.session

import pytest
from cc_sdk.put_object_input import PutObjectInput
from cc_sdk.store_type import StoreType
from cc_sdk.object_state import ObjectState

# pylint: disable=redefined-outer-name


@pytest.fixture
def put_object_input():
    return PutObjectInput(
        file_name="test",
        file_extension="txt",
        dest_store_type=StoreType.S3,
        object_state=ObjectState.LOCAL_DISK,
        data=b"test data",
        source_root_path="/path/to/source",
        dest_root_path="/path/to/destination",
    )


def test_getters(put_object_input):
    assert put_object_input.file_name == "test"
    assert put_object_input.file_extension == "txt"
    assert put_object_input.dest_store_type == StoreType.S3
    assert put_object_input.object_state == ObjectState.LOCAL_DISK
    assert put_object_input.data == b"test data"
    assert put_object_input.source_root_path == "/path/to/source"
    assert put_object_input.dest_root_path == "/path/to/destination"


def test_setters(put_object_input):
    with pytest.raises(AttributeError):
        put_object_input.file_name = "new_name"
    with pytest.raises(AttributeError):
        put_object_input.file_extension = "new_ext"
    with pytest.raises(AttributeError):
        put_object_input.dest_store_type = StoreType.EBS
    with pytest.raises(AttributeError):
        put_object_input.object_state = ObjectState.MEMORY
    with pytest.raises(AttributeError):
        put_object_input.data = b"new data"
    with pytest.raises(AttributeError):
        put_object_input.source_root_path = "/new/source/path"
    with pytest.raises(AttributeError):
        put_object_input.dest_root_path = "/new/destination/path"

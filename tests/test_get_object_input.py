from attr.exceptions import FrozenInstanceError
from pytest import fixture, raises
from cc_sdk.get_object_input import GetObjectInput
from cc_sdk.store_type import StoreType

# pylint: disable=redefined-outer-name


@fixture
def input_obj():
    # Fixture to create a GetObjectInput object with valid arguments
    return GetObjectInput(
        file_name="test_file",
        file_extension=".txt",
        source_store_type=StoreType.S3,
        source_root_path="/path/to/object",
    )


def test_getters(input_obj):
    # Test the getters for a GetObjectInput object
    assert input_obj.file_name == "test_file"
    assert input_obj.file_extension == ".txt"
    assert input_obj.source_store_type == StoreType.S3
    assert input_obj.source_root_path == "/path/to/object"


def test_setters(input_obj):
    # Test that readonly attributes raise a FrozenInstanceError when written to
    with raises(FrozenInstanceError):
        input_obj.file_name = "new_name"
    with raises(FrozenInstanceError):
        input_obj.file_extension = ".md"
    with raises(FrozenInstanceError):
        input_obj.source_store_type = StoreType.S3
    with raises(FrozenInstanceError):
        input_obj.source_root_path = "/new/path/to/object"

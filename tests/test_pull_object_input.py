import pytest
from cc_sdk.pull_object_input import PullObjectInput
from cc_sdk.store_type import StoreType

# pylint: disable=redefined-outer-name


@pytest.fixture
def pull_object_input():
    return PullObjectInput(
        file_name="test_file",
        file_extension=".txt",
        source_store_type=StoreType.S3,
        source_root_path="/path/to/source",
        dest_root_path="/path/to/dest",
    )


def test_getters(pull_object_input):
    assert pull_object_input.file_name == "test_file"
    assert pull_object_input.file_extension == ".txt"
    assert pull_object_input.source_store_type == StoreType.S3
    assert pull_object_input.source_root_path == "/path/to/source"
    assert pull_object_input.dest_root_path == "/path/to/dest"


def test_setters(pull_object_input):
    with pytest.raises(AttributeError):
        pull_object_input.file_name = "new_file"
    with pytest.raises(AttributeError):
        pull_object_input.file_extension = ".csv"
    with pytest.raises(AttributeError):
        pull_object_input.source_store_type = StoreType.EBS
    with pytest.raises(AttributeError):
        pull_object_input.source_root_path = "/new/source/path"
    with pytest.raises(AttributeError):
        pull_object_input.dest_root_path = "/new/dest/path"

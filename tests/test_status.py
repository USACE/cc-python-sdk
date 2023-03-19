import json
import pytest
from attr.exceptions import FrozenInstanceError
from cc_sdk.status import Status, StatusLevel

# pylint: disable=redefined-outer-name


@pytest.fixture
def status():
    return Status(0, StatusLevel.COMPUTING)


def test_getters(status):
    assert status.progress == 0
    assert status.status_level == StatusLevel.COMPUTING


def test_setters(status):
    with pytest.raises(FrozenInstanceError):
        status.progress = 1

    with pytest.raises(FrozenInstanceError):
        status.status_level = StatusLevel.FAILED


def test_bounds():
    with pytest.raises(ValueError):
        _ = Status(-1, StatusLevel.COMPUTING)
    with pytest.raises(ValueError):
        _ = Status(101, StatusLevel.COMPUTING)


def test_serialize(status):
    expected_json = json.dumps({"progress": 0, "status_level": "COMPUTING"})
    assert expected_json == status.serialize()
    assert json.loads(status.serialize()) == json.loads(expected_json)

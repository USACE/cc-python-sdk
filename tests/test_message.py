from cc_sdk.message import Message
import json
import pytest
from attr.exceptions import FrozenInstanceError


@pytest.fixture
def message():
    return Message("test message")


def test_getters(message):
    assert message.message == "test message"


def test_setters(message):
    with pytest.raises(FrozenInstanceError):
        message.message = "new message"


def test_serialize(message):
    expected_json = json.dumps({"message": "test message"})
    assert expected_json == message.serialize()
    assert json.loads(message.serialize()) == json.loads(expected_json)

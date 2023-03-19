import json
import pytest
from attr.exceptions import FrozenInstanceError
from cc_sdk.seed_set import SeedSet

# pylint: disable=redefined-outer-name


@pytest.fixture
def seed_set():
    return SeedSet(123, 321)


def test_getters(seed_set):
    assert seed_set.event_seed == 123
    assert seed_set.realization_seed == 321


def test_setters(seed_set):
    with pytest.raises(FrozenInstanceError):
        seed_set.event_seed = 456
    with pytest.raises(FrozenInstanceError):
        seed_set.realization_seed = 654


def test_serialize(seed_set):
    expected_json = json.dumps({"event_seed": 123, "realization_seed": 321})
    assert expected_json == seed_set.serialize()
    assert json.loads(seed_set.serialize()) == json.loads(expected_json)

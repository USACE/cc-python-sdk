import json
import pytest
from cc_sdk import Payload, DataSource, DataStore, StoreType


@pytest.fixture
def payload():
    return Payload(
        attributes={"attr1": "value1", "attr2": 2},
        stores=[
            DataStore(
                name="store1",
                id="store_id1",
                parameters={"param1": "value1"},
                store_type=StoreType.S3,
                ds_profile="profile1",
            ),
            DataStore(
                name="store2",
                id="store_id2",
                parameters={"param2": "value2"},
                store_type=StoreType.S3,
                ds_profile="profile2",
            ),
        ],
        inputs=[
            DataSource(
                name="input1",
                id="input_id1",
                store_name="store1",
                paths=["/path/to/data1"],
            ),
            DataSource(
                name="input2",
                id="input_id2",
                store_name="store2",
                paths=["/path/to/data2"],
            ),
        ],
        outputs=[
            DataSource(
                name="output1",
                id="output_id1",
                store_name="store1",
                paths=["/path/to/output1"],
            ),
            DataSource(
                name="output2",
                id="output_id2",
                store_name="store2",
                paths=["/path/to/output2"],
            ),
        ],
    )


def test_attributes_getter(payload):
    assert payload.attributes == {"attr1": "value1", "attr2": 2}


def test_stores_getter(payload):
    assert len(payload.stores) == 2
    assert payload.stores[0].name == "store1"
    assert payload.stores[1].name == "store2"


def test_inputs_getter(payload):
    assert len(payload.inputs) == 2
    assert payload.inputs[0].name == "input1"
    assert payload.inputs[1].name == "input2"


def test_outputs_getter(payload):
    assert len(payload.outputs) == 2
    assert payload.outputs[0].name == "output1"
    assert payload.outputs[1].name == "output2"


def test_attributes_setter_frozen(payload):
    with pytest.raises(AttributeError):
        payload.attributes = {"attr1": "new_value1", "attr2": 3}


def test_inputs_setter_frozen(payload):
    with pytest.raises(AttributeError):
        payload.inputs[0].paths = ["/path/to/new_input"]


def test_outputs_setter_frozen(payload):
    with pytest.raises(AttributeError):
        payload.outputs[0].paths = ["/path/to/new_output"]


def test_stores_setter(payload):
    store = DataStore(
        name="new_store",
        id="new_store_id",
        parameters={"param": "value"},
        store_type=StoreType.S3,
        ds_profile="profile",
    )
    payload.set_store(0, store)
    assert payload.stores[0].name == "new_store"


def test_serialize(payload):
    serialized = payload.serialize()
    expected = '{"attributes": {"attr1": "value1", "attr2": 2}, "stores": [{"name": "store1", "id": "store_id1", "parameters": {"param1": "value1"}, "store_type": "S3", "ds_profile": "profile1", "session": null}, {"name": "store2", "id": "store_id2", "parameters": {"param2": "value2"}, "store_type": "S3", "ds_profile": "profile2", "session": null}], "inputs": [{"name": "input1", "id": "input_id1", "store_name": "store1", "paths": ["/path/to/data1"]}, {"name": "input2", "id": "input_id2", "store_name": "store2", "paths": ["/path/to/data2"]}], "outputs": [{"name": "output1", "id": "output_id1", "store_name": "store1", "paths": ["/path/to/output1"]}, {"name": "output2", "id": "output_id2", "store_name": "store2", "paths": ["/path/to/output2"]}]}'
    assert serialized == expected

import json
from typing import Any, Type
from attr import define, field, setters, asdict, validators
from .data_source import DataSource
from .data_store import DataStore
from .json_encoder import EnumEncoder
from .validators import validate_homogeneous_list, validate_serializable


@define(auto_attribs=True)
class Payload:
    """
    A class that represents a payload for cloud compute.

    Attributes:
    - attributes : dict[str, Any]
        A dictionary of attributes for the payload. readonly
    - stores : list[DataStore]
        A list of DataStores.
    - inputs : list[DataSource]
        The inputs for the payload. readonly
    - inputs : list[DataSource]
        The outputs for the payload. readonly

    Methods:
    - serialize(): Returns a JSON string representation of the class.

    Raises:
    - ValueError:
        If a non-serializable object is set for an attribute.
    - TypeError:
        If the wrong type of object is set for an attribute.
    - AttributeError:
        If any readonly attribute is written to.
    """

    attributes: dict[str, Any] = field(
        on_setattr=setters.frozen,
        validator=[validators.instance_of(dict), validate_serializable],
    )
    stores: list[DataStore] = field(
        validator=[
            lambda instance, attribute, value: validate_homogeneous_list(
                instance, attribute, value, DataStore
            )
        ]
    )
    inputs: list[DataSource] = field(
        on_setattr=setters.frozen,
        validator=[
            lambda instance, attribute, value: validate_homogeneous_list(
                instance, attribute, value, DataSource
            )
        ],
    )
    outputs: list[DataSource] = field(
        on_setattr=setters.frozen,
        validator=[
            lambda instance, attribute, value: validate_homogeneous_list(
                instance, attribute, value, DataSource
            )
        ],
    )

    def set_store(self, index: int, store: DataStore) -> None:
        self.stores[index] = store

    def serialize(self) -> str:
        """
        Serializes the class as a json string

        Returns:
        - str: JSON string representation of the attributes
        """
        return json.dumps(asdict(self, recurse=True), cls=EnumEncoder)

    @staticmethod
    def from_json(json_str: str):
        """
        Converts a JSON string to a Payload object.

        Args:
            json_str (str): The JSON string to convert.

        Returns:
            Payload: The deserialized Payload object.

        Raises:
            JSONDecodeError: If the JSON string cannot be decoded.

        Example:
            >>> json_str = '{"attributes": {"attr1": "value1", "attr2": 2}, "stores": [{"name": "store1", "id": "store_id1", "parameters": {"param1": "value1"}, "store_type": "S3", "ds_profile": "profile1", "session": null}], "inputs": [{"name": "input1", "id": "input_id1", "store_name": "store1", "paths": ["/path/to/data1"]}], "outputs": [{"name": "output1", "id": "output_id1", "store_name": "store1", "paths": ["/path/to/output1"]}]}'
            >>> payload = Payload.from_json(json_str)
        """
        json_dict = json.loads(json_str)
        stores = [DataStore(**store) for store in json_dict["stores"]]
        inputs = [DataSource(**input) for input in json_dict["inputs"]]
        outputs = [DataSource(**output) for output in json_dict["outputs"]]
        return Payload(
            attributes=json_dict["attributes"],
            stores=stores,
            inputs=inputs,
            outputs=outputs,
        )

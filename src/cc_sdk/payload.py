import json
from typing import Any
from attr import define, field, setters, asdict, validators, filters, fields
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
        # assignment op does work, pylint just doesn't know it
        # pylint: disable=unsupported-assignment-operation
        self.stores[index] = store

    def serialize(self) -> str:
        """
        Serializes the class as a json string

        Returns:
        - str: JSON string representation of the attributes
        """
        # TODO, should we serialize to camelCase for attribute names?
        # do not serialize DataStore.session
        return json.dumps(
            asdict(
                self, recurse=True, filter=filters.exclude(fields(DataStore).session)
            ),
            cls=EnumEncoder,
        )

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

        """
        # TODO should we expect camelCase for attribute names?
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

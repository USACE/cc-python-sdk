from attr import define, field, setters, asdict, validators
import json
from .data_source import DataSource
from .data_store import DataStore
from .store_type import StoreTypeEncoder
from .validators import validate_serializable


def validate_stores(instance, attribute, value):
    if not isinstance(value, list):
        raise ValueError(f"stores must be a list of DataStores")
    if not all(isinstance(store, DataStore) for store in value):
        raise ValueError(f"stores must be a list of DataStores")


def validate_sources(instance, attribute, value):
    if not isinstance(value, list):
        raise ValueError(f"attribute must be a list of DataSources")
    if not all(isinstance(ds, DataSource) for ds in value):
        raise ValueError(f"attribute must be a list of DataSources")


@define(auto_attribs=True)
class Payload:
    """
    A class that represents a payload for cloud compute.

    Attributes:
    - attributes : dict[str, any]
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

    attributes: dict[str, any] = field(
        on_setattr=setters.frozen,
        validator=[validators.instance_of(dict), validate_serializable],
    )
    stores: list[DataStore] = field(validator=[validate_stores])
    inputs: list[DataSource] = field(
        on_setattr=setters.frozen,
        validator=[validate_sources],
    )
    outputs: list[DataSource] = field(
        on_setattr=setters.frozen,
        validator=[validate_sources],
    )

    def set_store(self, index: int, store: DataStore):
        self.stores[index] = store

    def serialize(self):
        """
        Serializes the class as a json string

        Returns:
        - str: JSON string representation of the attributes
        """
        return json.dumps(asdict(self), cls=StoreTypeEncoder)

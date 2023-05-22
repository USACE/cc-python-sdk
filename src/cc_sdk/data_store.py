import json
from typing import Any
from attr import define, field, setters, asdict, validators, filters, fields
from .validators import validate_serializable
from .store_type import StoreType
from .json_encoder import EnumEncoder


def convert_store_type(_, all_fields):
    results = []
    for the_field in all_fields:
        if the_field.converter is not None:
            results.append(the_field)
            continue
        if the_field.type in {StoreType, "store_type"}:
            converter = lambda s: StoreType.__members__[s] if isinstance(s, str) else s
        else:
            converter = None
        results.append(the_field.evolve(converter=converter))
    return results


@define(auto_attribs=True, field_transformer=convert_store_type)
class DataStore:
    """
    A class that represents a data store and its attributes.

    Attributes:
    - name : str
        The name of the data store. readonly
    - id : str
        The ID of the data store. readonly
    - parameters : dict[str, str]
        The parameters of the data store represented as a dictionary. readonly
    - store_type : StoreType
        The type of the data store. readonly
    - ds_profile : str
        The profile of the data store. readonly
    - session : any, optional
        The session object of the data store. It must be JSON serializable.

    Methods:
    - serialize(): Returns a JSON string representation of the attributes.

    Raises:
    - ValueError:
        If a non-serializable object is set for an attribute.
    - TypeError:
        If the wrong type of object is set for an attribute.
    - AttributeError:
        If any readonly attribute is written to.
    """

    name: str = field(
        on_setattr=setters.frozen, validator=[validators.instance_of(str)]
    )
    id: str = field(on_setattr=setters.frozen, validator=[validators.instance_of(str)])
    parameters: dict[str, str] = field(
        on_setattr=setters.frozen,
        validator=[validators.instance_of(dict), validate_serializable],
    )
    store_type: StoreType = field(
        on_setattr=setters.frozen, validator=[validators.instance_of(StoreType)]
    )
    ds_profile: str = field(
        on_setattr=setters.frozen, validator=[validators.instance_of(str)]
    )
    session: Any = field(default=None)

    def serialize(self) -> str:
        """
        Serializes the class as a json string

        Returns:
        - str: JSON string representation of the attributes
        """
        # do not serialize the session object
        return json.dumps(
            asdict(self, filter=filters.exclude(fields(DataStore).session)),
            cls=EnumEncoder,
        )

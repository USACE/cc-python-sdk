from attr import define, field, setters, asdict, validators
import json
from .validators import validate_serializable
from .store_type import StoreType, StoreTypeEncoder

@define(auto_attribs=True)
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
    session: any = field(default=None, validator=[validate_serializable])

    def serialize(self):
        """
        Serializes the class as a json string

        Returns:
        - str: JSON string representation of the attributes
        """
        return json.dumps(asdict(self), cls=StoreTypeEncoder)

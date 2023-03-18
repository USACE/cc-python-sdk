from attr import define, field, asdict, validators
import json
from .validators import validate_string_list


@define(auto_attribs=True, frozen=True)
class DataSource:
    """
    A class that represents a data source and its attributes.

    Attributes:
    - name : str
        The name of the data source. readonly
    - id : str
        The ID of the data source. readonly
    - store_name : str
        The name of the data store used by this data source. readonly
    - paths : List[str]
        The paths to the data in this data source. readonly

    Methods:
    - serialize(): Returns a JSON string representation of the attributes.

    Raises:
    - ValueError:
        If a non-serializable object is set for the session attribute.
    - TypeError:
        If the wrong type of object is set for an attribute.
    - FrozenInstanceError:
        If any attribute is written to.
    """

    name: str = field(validator=[validators.instance_of(str)])
    id: str = field(validator=[validators.instance_of(str)])
    store_name: str = field(
        validator=[validators.instance_of(str)],
    )
    paths: list[str] = field(validator=[validate_string_list])

    def serialize(self):
        """
        Serializes the class as a json string

        Returns:
        - str: JSON string representation of the attributes
        """
        return json.dumps(asdict(self))

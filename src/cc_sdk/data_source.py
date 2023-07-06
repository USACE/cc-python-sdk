import json
from attr import define, field, asdict, validators
from .validators import validate_homogeneous_list


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
        The paths to datasets in this data source. readonly
    - data_paths : List[str]
        The 'data paths' (paths to data within a dataset) in this data source. readonly

    Methods:
    - serialize(): Returns a JSON string representation of the attributes.

    Raises:
    - ValueError:
        If a non-serializable object is set for the attribute.
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
    paths: list[str] = field(
        validator=[
            lambda instance, attribute, value: validate_homogeneous_list(
                instance, attribute, value, str
            )
        ]
    )
    data_paths: list[str] = field(
        validator=[
            lambda instance, attribute, value: validate_homogeneous_list(
                instance, attribute, value, str
            )
        ]
    )

    def serialize(self) -> str:
        """
        Serializes the class as a json string

        Returns:
        - str: JSON string representation of the attributes
        """
        return json.dumps(asdict(self))

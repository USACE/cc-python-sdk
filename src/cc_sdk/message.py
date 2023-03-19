import json
from attrs import define, field, validators, asdict


@define(auto_attribs=True, frozen=True)
class Message:
    """
      A class that represents an error for the logger.

    Attributes:
    - message : str
        The message as a string. readonly

    Methods:
    - serialize(): Returns a JSON string representation of the attributes.

    Raises:
    - TypeError:
        If the wrong type of object is set for an attribute.
    - FrozenInstanceError:
        If any attribute is written to.
    """

    message: str = field(validator=[validators.instance_of(str)])

    def serialize(self) -> str:
        """
        Serializes the class as a json string
        Returns:
        - str: JSON string representation of the attributes
        """
        return json.dumps(asdict(self))

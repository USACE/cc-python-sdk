import json
from attrs import define, field, validators, asdict


@define(auto_attribs=True, frozen=True)
class SeedSet:
    """
      A class that represents a seed set for a computation.

    Attributes:
    - event_seed : int
        The seed as an integer. readonly
    - realization_seed : int
        The realized seed as an integer. readonly

    Methods:
    - serialize(): Returns a JSON string representation of the attributes.

    Raises:
    - TypeError:
        If the wrong type of object is set for an attribute.
    - FrozenInstanceError:
        If any attribute is written to.
    """

    event_seed: int = field(validator=[validators.instance_of(int)])
    realization_seed: int = field(validator=[validators.instance_of(int)])

    def serialize(self) -> str:
        """
        Serializes the class as a json string
        Returns:
        - str: JSON string representation of the attributes
        """
        return json.dumps(asdict(self))

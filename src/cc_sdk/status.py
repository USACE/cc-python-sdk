from enum import Enum
import json
from attrs import define, field, validators, asdict
from .json_encoder import EnumEncoder
from .validators import validate_range


class StatusLevel(Enum):
    """
    The StatusLevel class is an enum representing different status levels of
    a computation. The following status levels are available:

    Computing: currently computing
    FAILED: failed to complete
    SUCCEEDED: completed successfully

    The enum values serialize to a string representation of the enum name,
    instead of the integer value, to improve readability and prevent errors
    when deserializing.
    """

    COMPUTING = "COMPUTING"
    FAILED = "FAILED"
    SUCCEEDED = "SUCCEEDED"


def convert_status_level(_, fields):
    results = []
    for the_field in fields:
        if the_field.converter is not None:
            results.append(the_field)
            continue
        if the_field.type in {StatusLevel, "status_level"}:
            converter = (
                lambda s: StatusLevel.__members__[s] if isinstance(s, str) else s
            )
        else:
            converter = None
        results.append(the_field.evolve(converter=converter))
    return results


@define(auto_attribs=True, frozen=True, field_transformer=convert_status_level)
class Status:
    """
      A class that represents a status for a computation.

    Attributes:
    - progress : int
        The progress of the computation as a percent 0-100. readonly
    - status : StatusLevel
        The status level of the computation. readonly

    Methods:
    - serialize(): Returns a JSON string representation of the attributes.

    Raises:
    - TypeError:
        If the wrong type of object is set for an attribute.
    - FrozenInstanceError:
        If any attribute is written to.
    """

    progress: int = field(
        validator=[
            validators.instance_of(int),
            lambda instance, attribute, value: validate_range(
                instance, attribute, value, 0, 100
            ),
        ]
    )
    status_level: StatusLevel = field(validator=[validators.instance_of(StatusLevel)])

    def serialize(self) -> str:
        """
        Serializes the class as a json string
        Returns:
        - str: JSON string representation of the attributes
        """
        return json.dumps(asdict(self), cls=EnumEncoder)

from enum import Enum
import json
from typing import Final
from functools import total_ordering
from attrs import define, field, validators, asdict
from .json_encoder import EnumEncoder


@total_ordering
class ErrorLevel(Enum):
    """
    The ErrorLevel class is an enum representing different levels of error. The
    following error levels are available:

    DEBUG: a debug statement
    INFO: some information
    WARN: a warning
    ERROR: an error
    FATAL: a fatal message
    PANIC: a paniced state
    DISABLED: no messages will be reported

    The enum has an ordering from least severe to most severe

    The enum values serialize to a string representation of the enum name,
    instead of the integer value, to improve readability and prevent errors
    when deserializing.
    """

    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3
    FATAL = 4
    PANIC = 5
    DISABLED = 6

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.value < other.value
        return NotImplemented


# a set of all the enum values in the ErrorLevel enum is namespaced by the
# ErrorLevelOptions class
class ErrorLevelOptions:
    ALL_OPS: Final[set[ErrorLevel]] = set(ErrorLevel)


def convert_error_level(_, fields):
    results = []
    for the_field in fields:
        if the_field.converter is not None:
            results.append(the_field)
            continue
        if the_field.type in {ErrorLevel, "error_level"}:
            converter = lambda s: ErrorLevel.__members__[s] if isinstance(s, str) else s
        else:
            converter = None
        results.append(the_field.evolve(converter=converter))
    return results


@define(auto_attribs=True, frozen=True, field_transformer=convert_error_level)
class Error:
    """
      A class that represents an error for the logger.

    Attributes:
    - error : str
        The error message as a string. readonly
    - error_level : ErrorLevel
        The error level of the error. readonly

    Methods:
    - serialize(): Returns a JSON string representation of the attributes.

    Raises:
    - TypeError:
        If the wrong type of object is set for an attribute.
    - FrozenInstanceError:
        If any attribute is written to.
    """

    error: str = field(validator=[validators.instance_of(str)])
    error_level: ErrorLevel = field(validator=[validators.instance_of(ErrorLevel)])

    def serialize(self) -> str:
        """
        Serializes the class as a json string
        Returns:
        - str: JSON string representation of the attributes
        """
        return json.dumps(asdict(self), cls=EnumEncoder)

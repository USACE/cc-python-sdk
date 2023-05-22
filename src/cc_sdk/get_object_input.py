from attr import define, field, validators
from .store_type import StoreType


@define(auto_attribs=True, frozen=True)
class GetObjectInput:
    """
    A class that represents an input to the CCStore.GetObject command.
    This command will return bytes in memory.

    Attributes:
    - file_name : str
        The file name of the object to pull not including its extension. readonly
    - file_extension : str
        The extension of the file to pull. readonly
    - source_store_type : StoreType
        The type of data store the object will be pulled from
        (does not include file name or extension). readonly
    - source_root_path : string
        The source path of the object on the data store
        (does not include file name or extension). readonly

    Raises:
    - TypeError:
        If the wrong type of object is set for an attribute.
    - FrozenInstanceError:
        If any readonly attribute is written to.
    """

    file_name: str = field(validator=[validators.instance_of(str)])
    file_extension: str = field(validator=[validators.instance_of(str)])
    source_store_type: StoreType = field(
        validator=[validators.instance_of(StoreType)],
    )
    source_root_path: str = field(validator=validators.instance_of(str))

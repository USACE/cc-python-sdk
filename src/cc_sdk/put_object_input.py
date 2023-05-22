from attr import define, field, validators
from .store_type import StoreType
from .object_state import ObjectState


@define(auto_attribs=True, frozen=True)
class PutObjectInput:
    """
    A class that represents an input to the CCStore.PutObject command.

    Attributes:
    - file_name : str
        The file name of the object to put not including its extension. readonly
    - file_extension : str
        The extension of the file to put. readonly
    - dest_store_type : StoreType
        The type of data store the object will be put in. readonly
    - object_state : ObjectState
        The storage state of the object. readonly
    - data : bytes
        The raw bytes of the data. readonly. optional, but required for in memory files.
    - source_root_path : string
        The source directory path of the object (includes file name or extension). readonly
        optional, but required for local disk files.
    - dest_root_path : string
        The destination directory path of the object on the data store (includes file name or extension). readonly

    Raises:
    - TypeError:
        If the wrong type of object is set for an attribute.
    - FrozenInstanceError:
        If any readonly attribute is written to.
    """

    file_name: str = field(validator=[validators.instance_of(str)])
    file_extension: str = field(validator=[validators.instance_of(str)])
    dest_store_type: StoreType = field(
        validator=[validators.instance_of(StoreType)],
    )
    object_state: ObjectState = field(validator=validators.instance_of(ObjectState))
    dest_root_path: str = field(validator=validators.instance_of(str))
    source_root_path: str = field(default="", validator=validators.instance_of(str))
    data: bytes = field(default=bytes(), validator=validators.instance_of(bytes))

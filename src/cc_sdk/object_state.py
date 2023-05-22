from enum import Enum


class ObjectState(Enum):
    """
    The ObjectState class is an enum representing storage state of the object.
    The following states are available:

    Memory: Object stored in memory
    LocalDisk: Object stored on local filesystem
    RemoteDisk: TODO

    Each state has an associated integer value.

    The enum values serialize to a string representation of the enum name,
    instead of the integer value, to improve readability and prevent errors
    when deserializing.
    """

    MEMORY = "MEMORY"
    LOCAL_DISK = "LOCAL_DISK"
    # REMOTE_DISK = "REMOTE_DISK"

from enum import Enum


class StoreType(Enum):
    """
    The StoreType class is an enum representing different types of data stores. The following store types are available:

    S3: Amazon S3 data store
    WS: ??? Need to ask Will
    RDBMS: Relational database management system data store
    EBS: Elastic Block Store data store

    Each store type has an associated integer value, with S3 having a value of 0, WS having a value of 1, RDBMS having
    a value of 2, and EBS having a value of 3. This class can be used to ensure type safety when working with different
    data stores.

    The enum values serialize to a string representation of the enum name, instead of the integer value, to improve
    readability and prevent errors when deserializing.
    """

    S3 = "S3"
    WS = "WS"
    RDBMS = "RDBMS"
    EBS = "EBS"

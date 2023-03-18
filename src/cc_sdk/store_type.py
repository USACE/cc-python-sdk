from enum import Enum
import json

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
    S3 = 0
    WS = 1
    RDBMS = 2
    EBS = 3

class StoreTypeEncoder(json.JSONEncoder):
    """
    The StoreTypeEncoder is a custom JSON encoder that extends the default json.JSONEncoder class to handle the serialization of StoreType Enum values.

    It overrides the default() method of the JSONEncoder class to handle StoreType objects by returning their name attribute instead of the object itself. This ensures that StoreType objects are serialized to a JSON string that represents their name.

    Usage:
        To use this encoder, pass it as the cls argument when calling json.dumps(), as shown below:

        ```
        import json
        from .store_type import StoreTypeEncoder

        data = {"store_type": StoreType.S3}
        json_string = json.dumps(data, cls=StoreTypeEncoder)
        ```

    Raises:
        - TypeError:
            If an object of an unsupported type is encountered.
    """
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        return json.JSONEncoder.default(self, obj)
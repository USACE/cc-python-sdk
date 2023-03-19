import json
from enum import Enum


class EnumEncoder(json.JSONEncoder):
    """
    The EnumEncoder is a custom JSON encoder that extends the default json.JSONEncoder class to handle the
    serialization of Enum values.

    It overrides the default() method of the JSONEncoder class to handle Enum objects by returning their name
    attribute instead of the object itself. This ensures that Enum objects are serialized to a JSON string that
    represents their name.

    Usage:
        To use this encoder, pass it as the cls argument when calling json.dumps(), as shown below:

        ```
        import json
        from .json_encoder import EnumEncoder

        data = {"store_type": StoreType.S3}
        json_string = json.dumps(data, cls=EnumEncoder)
        ```

    Raises:
        - TypeError:
            If an object of an unsupported type is encountered.
    """

    def default(self, o):
        if isinstance(o, Enum):
            return o.name
        return json.JSONEncoder.default(self, o)

import json


def validate_serializable(instance, attribute, value):
    """
    A validator that ensures an attribute is JSON serializable.

    Parameters:
    -----------
    instance : class
        The instance of the class.
    attribute : str
        The name of the attribute.
    value : any
        The value of the attribute.

    Raises:
    -------
    ValueError:
        If a non-serializable object is set for the attribute.
    """
    try:
        json.dumps(value)
    except TypeError:
        raise ValueError(f"Session attribute must be JSON serializable")


def validate_string_list(instance, attribute, value):
    if not isinstance(value, list):
        raise ValueError(f"paths must be a list of strings")
    if not all(isinstance(path, str) for path in value):
        raise ValueError(f"paths must be a list of strings")

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
        If an incorrect value is set for the attribute.
    """
    try:
        json.dumps(value)
    except TypeError:
        raise ValueError(f"Attributes must be JSON serializable")


def validate_range(instance, attribute, value, lower_bound, upper_bound):
    """
    A validator that ensures an value is great than or less than a set of
    bounding variables.

    Parameters:
    -----------
    instance : class
        The instance of the class.
    attribute : str
        The name of the attribute.
    value : any
        The value of the attribute.
    lower_bound : any
        The lower bound on the value of the attribute.
    upper_bound : any
        The upper bound on the value of the attribute.

    Raises:
    -------
    ValueError:
        If an incorrect value is set for the attribute.
    """
    if value > upper_bound or value < lower_bound:
        raise ValueError("Value out of bounds")


def validate_homogeneous_list(instance, attribute, value, type):
    """
    A validator that ensures an attribute is a list of strings

    Parameters:
    -----------
    instance : class
        The instance of the class.
    attribute : str
        The name of the attribute.
    value : any
        The value of the attribute.
    type: Type
        The type of the elements of the list.

    Raises:
    -------
    ValueError:
        If an incorrect value is set for the attribute.
    """
    if not isinstance(value, list):
        raise ValueError(f"{str(attribute)} must be a list of {str(type)}")
    if not all(isinstance(path, type) for path in value):
        raise ValueError(f"{str(attribute)} must be a list of {str(type)}")

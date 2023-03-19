import json
from attr import define, field, asdict, validators


@define(auto_attribs=True)
class AWSConfig:
    """
    This class provides configuration settings for using an AWS S3 data store.

    Attributes:
    - aws_config_name: str
        The name of the AWS configuration (optional).
    - aws_access_key_id : str
        The AWS access key ID to use for accessing the data store (optional).
    - aws_secret_access_key_id : str
        The AWS secret access key ID to use for accessing the data store (optional).
    - aws_region : str
        The AWS region where the data store is located (optional).
    - aws_bucket : str
        The name of the AWS S3 bucket to use as the data store (optional).
    - aws_mock : bool
        Whether to use a mock AWS S3 data store (optional, default is False).
    - aws_endpoint : str
        The endpoint URL for the AWS S3 data store (optional).
    - aws_disable_ssl : bool
        Whether to disable SSL when connecting to the AWS S3 data store (optional, default is False).
    - aws_force_path_style : bool
        Whether to use path-style addressing for the AWS S3 data store (optional, default is False).

    Methods:
    - serialize(): Returns a JSON string representation of the attributes.

    Raises:
    - TypeError:
        If the wrong type of object is set for an attribute.
    """

    aws_config_name: str = field(default="", validator=[validators.instance_of(str)])
    aws_access_key_id: str = field(default="", validator=[validators.instance_of(str)])
    aws_secret_access_key_id: str = field(
        default="", validator=[validators.instance_of(str)]
    )
    aws_region: str = field(default="", validator=[validators.instance_of(str)])
    aws_bucket: str = field(default="", validator=[validators.instance_of(str)])
    aws_mock: bool = field(default=False, validator=[validators.instance_of(bool)])
    aws_endpoint: str | None = field(
        default=None, validator=[validators.instance_of(str | None)]
    )
    aws_disable_ssl: bool = field(
        default=False, validator=[validators.instance_of(bool)]
    )
    aws_force_path_style: bool = field(
        default=False, validator=[validators.instance_of(bool)]
    )

    def serialize(self) -> str:
        """
        Serializes the AWSConfig object to a JSON string.

        Returns:
            str: JSON string representation of the attributes.
        """
        return json.dumps(asdict(self))

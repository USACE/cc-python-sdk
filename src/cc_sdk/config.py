import json
from attrs import define, field, asdict
from .aws_config import AWSConfig
from .validators import validate_homogeneous_list


@define(auto_attribs=True)
class Config:
    """
    Stores the configurations for various data stores

      Attributes:
      - aws_configs : list[AWSConfig]
          The configs for AWS

      Raises:
      - TypeError:
          If the wrong type of object is set for an attribute.
    """

    aws_configs: list[AWSConfig] = field(
        validator=[
            lambda instance, attribute, value: validate_homogeneous_list(
                instance, attribute, value, AWSConfig
            )
        ]
    )

    def serialize(self) -> str:
        """
        Serializes the class as a json string

        Returns:
        - str: JSON string representation of the attributes
        """
        return json.dumps(asdict(self, recurse=True))

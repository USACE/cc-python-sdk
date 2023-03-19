import json
import pytest
from cc_sdk import AWSConfig

# pylint: disable=redefined-outer-name


@pytest.fixture
def aws_config():
    return AWSConfig(
        aws_config_name="test",
        aws_access_key_id="my_access_key",
        aws_secret_access_key_id="my_secret_key",
        aws_region="us-west-2",
        aws_bucket="my_bucket",
        aws_mock=True,
        aws_endpoint="https://my-endpoint.com",
        aws_disable_ssl=True,
        aws_force_path_style=True,
    )


def test_getters(aws_config):
    assert aws_config.aws_config_name == "test"
    assert aws_config.aws_access_key_id == "my_access_key"
    assert aws_config.aws_secret_access_key_id == "my_secret_key"
    assert aws_config.aws_region == "us-west-2"
    assert aws_config.aws_bucket == "my_bucket"
    assert aws_config.aws_mock is True
    assert aws_config.aws_endpoint == "https://my-endpoint.com"
    assert aws_config.aws_disable_ssl is True
    assert aws_config.aws_force_path_style is True


def test_setters(aws_config):
    aws_config.aws_config_name = "new_test"
    assert aws_config.aws_config_name == "new_test"

    aws_config.aws_access_key_id = "new_access_key"
    assert aws_config.aws_access_key_id == "new_access_key"

    aws_config.aws_secret_access_key_id = "new_secret_key"
    assert aws_config.aws_secret_access_key_id == "new_secret_key"

    aws_config.aws_region = "us-east-1"
    assert aws_config.aws_region == "us-east-1"

    aws_config.aws_bucket = "new_bucket"
    assert aws_config.aws_bucket == "new_bucket"

    aws_config.aws_mock = False
    assert aws_config.aws_mock is False

    aws_config.aws_endpoint = "https://new-endpoint.com"
    assert aws_config.aws_endpoint == "https://new-endpoint.com"

    aws_config.aws_disable_ssl = False
    assert aws_config.aws_disable_ssl is False

    aws_config.aws_force_path_style = False
    assert aws_config.aws_force_path_style is False


def test_serialize(aws_config):
    expected_json = '{"aws_config_name": "test", "aws_access_key_id": "my_access_key", "aws_secret_access_key_id": \
        "my_secret_key", "aws_region": "us-west-2", "aws_bucket": "my_bucket", "aws_mock": true, "aws_endpoint": \
            "https://my-endpoint.com", "aws_disable_ssl": true, "aws_force_path_style": true}'
    assert aws_config.serialize() == json.dumps(json.loads(expected_json))
    assert json.loads(aws_config.serialize()) == json.loads(expected_json)

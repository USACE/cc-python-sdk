import json
from pytest import fixture
from cc_sdk import AWSConfig, Config

# pylint: disable=redefined-outer-name


@fixture
def config():
    aws_config = AWSConfig(
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
    return Config(aws_configs=[aws_config])


def test_getters(config):
    aws_config = AWSConfig(
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
    assert config.aws_configs == [aws_config]


def test_setters(config):
    aws_config = AWSConfig(
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
    config.aws_configs = [aws_config]


def test_serialize(config):
    expected_json = '{"aws_configs": [{"aws_config_name": "test", "aws_access_key_id": "my_access_key", \
        "aws_secret_access_key_id": "my_secret_key", "aws_region": "us-west-2", "aws_bucket": "my_bucket", \
            "aws_mock": true, "aws_endpoint": "https://my-endpoint.com", "aws_disable_ssl": true, \
                "aws_force_path_style": true}]}'
    assert config.serialize() == json.dumps(json.loads(expected_json))
    assert json.loads(config.serialize()) == json.loads(expected_json)

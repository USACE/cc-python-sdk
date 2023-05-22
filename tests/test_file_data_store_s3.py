import io
import pytest
from moto import mock_s3
import boto3
from cc_sdk import (
    FileDataStoreS3,
    StoreType,
    environment_variables,
    DataStore,
)

# pylint: disable=redefined-outer-name


@pytest.fixture
def file_data_store(monkeypatch):
    with mock_s3():
        data_store = DataStore(
            name="testname",
            id="testid",
            parameters={"root": "testroot"},
            store_type=StoreType.S3,
            ds_profile="testprofile",
        )
        monkeypatch.setenv(
            "testprofile" + "_" + environment_variables.AWS_ACCESS_KEY_ID,
            "my_access_key",
        )
        monkeypatch.setenv(
            "testprofile" + "_" + environment_variables.AWS_SECRET_ACCESS_KEY,
            "my_secret_key",
        )
        monkeypatch.setenv(
            "testprofile" + "_" + environment_variables.AWS_DEFAULT_REGION,
            "us-west-2",
        )
        monkeypatch.setenv(
            "testprofile" + "_" + environment_variables.AWS_S3_BUCKET,
            "my_bucket",
        )
        monkeypatch.setenv(
            "testprofile" + "_" + environment_variables.S3_MOCK,
            "True",
        )
        monkeypatch.setenv(
            "testprofile" + "_" + environment_variables.S3_DISABLE_SSL,
            "True",
        )
        monkeypatch.setenv(
            "testprofile" + "_" + environment_variables.S3_FORCE_PATH_STYLE,
            "False",
        )

        # create a mock S3 client
        s3_client = boto3.client("s3")
        # create a mock S3 bucket
        s3_client.create_bucket(Bucket="my_bucket")

        file_data_store = FileDataStoreS3(data_store)

        yield file_data_store
        response = s3_client.list_objects_v2(Bucket="my_bucket")
        if "Contents" in response:
            delete_keys = [{"Key": obj["Key"]} for obj in response["Contents"]]
            s3_client.delete_objects(
                Bucket="my_bucket", Delete={"Objects": delete_keys}
            )
        s3_client.delete_bucket(Bucket="my_bucket")


def test_put(file_data_store):
    assert file_data_store.put(io.BytesIO(b"Hello"), "test") is True


def test_get(file_data_store):
    file_data_store.put(io.BytesIO(b"Hello"), "test")
    assert file_data_store.get("test").getvalue() == b"Hello"


def test_copy(file_data_store):
    file_data_store.put(io.BytesIO(b"Hello"), "test")
    file_data_store.copy(file_data_store, "test", "testcopy")
    assert file_data_store.get("testcopy").getvalue() == b"Hello"


def test_delete(file_data_store):
    assert file_data_store.put(io.BytesIO(b"Hello"), "test") is True
    file_data_store.delete("test")
    with pytest.raises(Exception):
        file_data_store.get("test")

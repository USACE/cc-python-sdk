import json
import pytest
from cc_sdk import (
    CCStoreS3,
    AWSConfig,
    StoreType,
    environment_variables,
    constants,
    PutObjectInput,
    PullObjectInput,
    GetObjectInput,
    ObjectState,
    Payload,
    DataSource,
    DataStore,
)
from unittest.mock import Mock
import tempfile
import os
import shutil
from moto import mock_s3
import boto3


def test_initialize(monkeypatch):
    monkeypatch.setenv(
        environment_variables.CC_PROFILE
        + "_"
        + environment_variables.AWS_ACCESS_KEY_ID,
        "my_access_key",
    )
    monkeypatch.setenv(
        environment_variables.CC_PROFILE
        + "_"
        + environment_variables.AWS_SECRET_ACCESS_KEY,
        "my_secret_key",
    )
    monkeypatch.setenv(
        environment_variables.CC_PROFILE
        + "_"
        + environment_variables.AWS_DEFAULT_REGION,
        "us-west-2",
    )
    monkeypatch.setenv(
        environment_variables.CC_PROFILE + "_" + environment_variables.AWS_S3_BUCKET,
        "my_bucket",
    )
    monkeypatch.setenv(
        environment_variables.CC_PROFILE + "_" + environment_variables.S3_ENDPOINT,
        "http://localhost:9000",
    )
    monkeypatch.setenv(environment_variables.CC_MANIFEST_ID, "my_manifest")
    monkeypatch.setenv(environment_variables.CC_ROOT, "my_root")
    monkeypatch.setenv(
        environment_variables.CC_PROFILE + "_" + environment_variables.S3_MOCK, "True"
    )

    # Set up mock for create_s3_client
    mock_create_s3_client = Mock()
    monkeypatch.setattr(CCStoreS3, "create_s3_client", mock_create_s3_client)
    store = CCStoreS3()
    # Assert that create_s3_client was called with the correct arguments
    mock_create_s3_client.assert_called_with(store.config)
    # Assert that the instance variables were set correctly
    assert isinstance(store.config, AWSConfig)
    assert store.config.aws_access_key_id == "my_access_key"
    assert store.config.aws_secret_access_key_id == "my_secret_key"
    assert store.config.aws_region == "us-west-2"
    assert store.config.aws_bucket == "my_bucket"
    assert store.config.aws_endpoint == "http://localhost:9000"
    assert store.manifest_id == "my_manifest"
    assert store.local_root_path == constants.LOCAL_ROOT_PATH
    assert store.bucket == "my_bucket"
    assert store.root == "my_root"
    assert store.store_type == StoreType.S3


def test_initialize_missing_required_env_var():
    with pytest.raises(EnvironmentError):
        CCStoreS3()


@pytest.fixture
def store(monkeypatch):
    with mock_s3():
        monkeypatch.setenv(
            environment_variables.CC_PROFILE
            + "_"
            + environment_variables.AWS_ACCESS_KEY_ID,
            "my_access_key",
        )
        monkeypatch.setenv(
            environment_variables.CC_PROFILE
            + "_"
            + environment_variables.AWS_SECRET_ACCESS_KEY,
            "my_secret_key",
        )
        monkeypatch.setenv(
            environment_variables.CC_PROFILE
            + "_"
            + environment_variables.AWS_DEFAULT_REGION,
            "us-west-2",
        )
        monkeypatch.setenv(
            environment_variables.CC_PROFILE
            + "_"
            + environment_variables.AWS_S3_BUCKET,
            "my_bucket",
        )
        monkeypatch.setenv(
            environment_variables.CC_PROFILE + "_" + environment_variables.S3_ENDPOINT,
            "http://localhost:9000",
        )
        monkeypatch.setenv(environment_variables.CC_MANIFEST_ID, "my_manifest")
        monkeypatch.setenv(environment_variables.CC_ROOT, "/tmp")
        monkeypatch.setenv(
            environment_variables.CC_PROFILE + "_" + environment_variables.S3_MOCK,
            "True",
        )
        monkeypatch.setenv(
            environment_variables.CC_PROFILE
            + "_"
            + environment_variables.S3_DISABLE_SSL,
            "True",
        )
        monkeypatch.setenv(
            environment_variables.CC_PROFILE
            + "_"
            + environment_variables.S3_FORCE_PATH_STYLE,
            "False",
        )

        # create a mock S3 client
        s3 = boto3.client("s3")
        # create a mock S3 bucket
        s3.create_bucket(Bucket="my_bucket")
        # create and return an instance of the Store class
        store = CCStoreS3()

        yield store
        response = s3.list_objects_v2(Bucket="my_bucket")
        if "Contents" in response:
            delete_keys = [{"Key": obj["Key"]} for obj in response["Contents"]]
            s3.delete_objects(Bucket="my_bucket", Delete={"Objects": delete_keys})
        s3.delete_bucket(Bucket="my_bucket")


def test_handles_data_store_type(store):
    assert store.handles_data_store_type(StoreType.S3) is True


def test_put_object_local_disk_file_not_found(store):
    input_data = {
        "file_name": "test_file",
        "file_extension": "txt",
        "dest_store_type": StoreType.S3,
        "object_state": ObjectState.LocalDisk,
        "data": bytes(),
        "source_path": "/no/file/here",
        "dest_path": "place/to/put/file",
    }
    with pytest.raises(FileNotFoundError):
        store.put_object(PutObjectInput(**input_data))


def test_put_object_local_disk_error_reading_file(store):
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(b"Hello, world!")
        tmp_file.flush()
        # Set the file permissions to read-only
        os.chmod(tmp_file.name, 0o400)

        input_data = {
            "file_name": os.path.basename(tmp_file.name),
            "file_extension": "",
            "dest_store_type": StoreType.S3,
            "object_state": ObjectState.LocalDisk,
            "data": bytes(),
            "source_path": os.path.dirname(tmp_file.name),
            "dest_path": "place/to/put/file",
        }

        # Check that an IOError is raised when `store.put_object` is called
        with pytest.raises(IOError):
            store.put_object(PutObjectInput(**input_data))

        # Set the file permissions back to read-write
        os.chmod(tmp_file.name, 0o600)

        # Clean up the temporary file
        os.remove(tmp_file.name)


@pytest.fixture
def temp_dir():
    temp_dir = "/tmp/my_manifest"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_put_object_local_disk_success(store, temp_dir):
    # Create a temporary file
    with tempfile.NamedTemporaryFile(dir=temp_dir) as tmp_file:
        tmp_file.write(b"Hello, world!")
        tmp_file.flush()
        object_key = "place/to/put/file/" + os.path.basename(tmp_file.name)
        input_data = {
            "file_name": os.path.basename(tmp_file.name),
            "file_extension": "",
            "dest_store_type": StoreType.S3,
            "object_state": ObjectState.LocalDisk,
            "data": bytes(),
            "source_path": tmp_file.name,
            "dest_path": object_key,
        }
        assert store.put_object(PutObjectInput(**input_data)) is True
        s3 = CCStoreS3.create_s3_client(store.config)
        objects = s3.list_objects_v2(Bucket="my_bucket", Prefix=object_key)
        assert any(
            obj["Key"] == object_key for obj in objects.get("Contents", [])
        ), f"Object '{object_key}' does not exist in bucket '{store.config.bucket}'"
        response = s3.get_object(Bucket="my_bucket", Key=object_key)
        assert (
            response["Body"].read() == b"Hello, world!"
        ), f"Object '{object_key}' in bucket '{store.config.bucket}' has unexpected contents"


def test_put_object_memory_success(store):
    object_key = "place/to/put/file/" + "memory_put_test"
    input_data = {
        "file_name": "memory_put_test",
        "file_extension": "",
        "dest_store_type": StoreType.S3,
        "object_state": ObjectState.Memory,
        "data": b"Hello, world!",
        "source_path": "memory",
        "dest_path": object_key,
    }
    assert store.put_object(PutObjectInput(**input_data)) is True
    s3 = CCStoreS3.create_s3_client(store.config)
    objects = s3.list_objects_v2(Bucket="my_bucket", Prefix=object_key)
    assert any(
        obj["Key"] == object_key for obj in objects.get("Contents", [])
    ), f"Object '{object_key}' does not exist in bucket '{store.config.bucket}'"
    response = s3.get_object(Bucket="my_bucket", Key=object_key)
    assert (
        response["Body"].read() == b"Hello, world!"
    ), f"Object '{object_key}' in bucket '{store.config.bucket}' has unexpected contents"


def test_pull_object_success(store, temp_dir):
    # put the object
    object_key = "place/to/put/file/" + "memory_put_test"
    input_data = {
        "file_name": "memory_put_test",
        "file_extension": "",
        "dest_store_type": StoreType.S3,
        "object_state": ObjectState.Memory,
        "data": b"Hello, world!",
        "source_path": "memory",
        "dest_path": object_key,
    }
    assert store.put_object(PutObjectInput(**input_data)) is True
    # pull the object
    input_data = {
        "file_name": "memory_put_test",
        "file_extension": "",
        "source_store_type": StoreType.S3,
        "source_root_path": "place/to/put/file",
        "dest_root_path": temp_dir,
    }
    assert store.pull_object(PullObjectInput(**input_data)) is True
    pulled_filepath = os.path.join(temp_dir, "memory_put_test")
    with open(pulled_filepath, "rb") as f:
        contents = f.read()
    assert (
        contents == b"Hello, world!"
    ), f"File at '{pulled_filepath}' has unexpected contents"


def test_pull_object_error(store, temp_dir):
    # pull the object that doesn't exist
    input_data = {
        "file_name": "not_a_real_file",
        "file_extension": "",
        "source_store_type": StoreType.S3,
        "source_root_path": "place/to/put/file",
        "dest_root_path": temp_dir,
    }
    assert store.pull_object(PullObjectInput(**input_data)) is False


def test_get_object_success(store):
    # put the object
    object_key = "place/to/put/file/" + "memory_put_test"
    input_data = {
        "file_name": "memory_put_test",
        "file_extension": "",
        "dest_store_type": StoreType.S3,
        "object_state": ObjectState.Memory,
        "data": b"Hello, world!",
        "source_path": "memory",
        "dest_path": object_key,
    }
    assert store.put_object(PutObjectInput(**input_data)) is True
    # pull the object
    input_data = {
        "file_name": "memory_put_test",
        "file_extension": "",
        "source_store_type": StoreType.S3,
        "source_root_path": "place/to/put/file",
    }
    assert store.get_object(GetObjectInput(**input_data)) == b"Hello, world!"


def test_get_object_error(store):
    with pytest.raises(Exception):
        # get the object that doesn't exist
        input_data = {
            "file_name": "not_a_real_file",
            "file_extension": "",
            "source_store_type": StoreType.S3,
            "source_root_path": "place/to/put/file",
        }
        _ = store.pull_object(PullObjectInput(**input_data))


@pytest.fixture
def payload():
    return Payload(
        attributes={"attr1": "value1", "attr2": 2},
        stores=[
            DataStore(
                name="store1",
                id="store_id1",
                parameters={"param1": "value1"},
                store_type=StoreType.S3,
                ds_profile="profile1",
            ),
            DataStore(
                name="store2",
                id="store_id2",
                parameters={"param2": "value2"},
                store_type=StoreType.S3,
                ds_profile="profile2",
            ),
        ],
        inputs=[
            DataSource(
                name="input1",
                id="input_id1",
                store_name="store1",
                paths=["/path/to/data1"],
            ),
            DataSource(
                name="input2",
                id="input_id2",
                store_name="store2",
                paths=["/path/to/data2"],
            ),
        ],
        outputs=[
            DataSource(
                name="output1",
                id="output_id1",
                store_name="store1",
                paths=["/path/to/output1"],
            ),
            DataSource(
                name="output2",
                id="output_id2",
                store_name="store2",
                paths=["/path/to/output2"],
            ),
        ],
    )


def test_read_json_model_payload_from_bytes(payload):
    payload_bytes = b'{"attributes": {"attr1": "value1", "attr2": 2}, "stores": [{"name": "store1", "id": "store_id1", "parameters": {"param1": "value1"}, "store_type": "S3", "ds_profile": "profile1", "session": null}, {"name": "store2", "id": "store_id2", "parameters": {"param2": "value2"}, "store_type": "S3", "ds_profile": "profile2", "session": null}], "inputs": [{"name": "input1", "id": "input_id1", "store_name": "store1", "paths": ["/path/to/data1"]}, {"name": "input2", "id": "input_id2", "store_name": "store2", "paths": ["/path/to/data2"]}], "outputs": [{"name": "output1", "id": "output_id1", "store_name": "store1", "paths": ["/path/to/output1"]}, {"name": "output2", "id": "output_id2", "store_name": "store2", "paths": ["/path/to/output2"]}]}'
    assert payload == CCStoreS3.read_json_model_payload_from_bytes(payload_bytes)


def test_get_payload(payload, store):
    # Create a temporary file for the payload and put on S3
    path = store.root + "/" + store.manifest_id + "/" + constants.PAYLOAD_FILE_NAME
    input_data = {
        "file_name": constants.PAYLOAD_FILE_NAME,
        "file_extension": "",
        "dest_store_type": StoreType.S3,
        "object_state": ObjectState.Memory,
        "data": payload.serialize().encode(),
        "source_path": "memory",
        "dest_path": path,
    }
    assert store.put_object(PutObjectInput(**input_data)) is True
    assert store.get_payload() == payload

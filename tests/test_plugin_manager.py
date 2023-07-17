import io
import os
import pytest
import boto3
from moto import mock_s3
from cc_sdk import (
    PluginManager,
    DataSource,
    DataStore,
    Payload,
    StoreType,
    environment_variables,
    CCStoreS3,
    FileDataStoreS3,
    PutObjectInput,
    ObjectState,
)

# pylint: disable=redefined-outer-name


@pytest.fixture
def payload():
    return Payload(
        attributes={"attr1": "value1", "attr2": 2},
        stores=[
            DataStore(
                name="store1",
                id="store_id1",
                parameters={"param1": "value1", "root": "store1_root"},
                store_type=StoreType.S3,
                ds_profile="profile1",
            ),
            DataStore(
                name="store2",
                id="store_id2",
                parameters={"param2": "value2", "root": "store2_root"},
                store_type=StoreType.S3,
                ds_profile="profile2",
            ),
        ],
        inputs=[
            DataSource(
                name="input1",
                id="input_id1",
                store_name="store1",
                paths=["path/to/data1"],
                data_paths=["{ENV::TEST_ENV_VAR}/path/to/{ATTR::attr1}"],
            ),
            DataSource(
                name="input2",
                id="input_id2",
                store_name="store2",
                paths=["path/to/data2"],
                data_paths=[],
            ),
        ],
        outputs=[
            DataSource(
                name="output1",
                id="output_id1",
                store_name="store1",
                paths=["path/to/output1"],
                data_paths=[],
            ),
            DataSource(
                name="output2",
                id="output_id2",
                store_name="store2",
                paths=["path/to/output2"],
                data_paths=[],
            ),
        ],
    )


@pytest.fixture
def plugin_manager(payload, monkeypatch):
    # CCStore Env vars
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
    monkeypatch.setenv(environment_variables.CC_MANIFEST_ID, "my_manifest")
    monkeypatch.setenv(environment_variables.CC_ROOT, "my_root")
    monkeypatch.setenv(
        environment_variables.CC_PROFILE + "_" + environment_variables.S3_MOCK, "True"
    )
    ## plugin env vars
    monkeypatch.setenv(environment_variables.CC_PLUGIN_DEFINITION, "test_plugin")
    monkeypatch.setenv(
        environment_variables.CC_EVENT_NUMBER,
        "000",
    )
    ## profile1 env vars
    monkeypatch.setenv(
        "profile1" + "_" + environment_variables.AWS_ACCESS_KEY_ID,
        "my_access_key",
    )
    monkeypatch.setenv(
        "profile1" + "_" + environment_variables.AWS_SECRET_ACCESS_KEY,
        "my_secret_key",
    )
    monkeypatch.setenv(
        "profile1" + "_" + environment_variables.AWS_DEFAULT_REGION,
        "us-west-2",
    )
    monkeypatch.setenv(
        "profile1" + "_" + environment_variables.AWS_S3_BUCKET,
        "my_bucket",
    )
    monkeypatch.setenv("profile1" + "_" + environment_variables.S3_MOCK, "True")
    ## profile2 env vars
    monkeypatch.setenv(
        "profile2" + "_" + environment_variables.AWS_ACCESS_KEY_ID,
        "my_access_key",
    )
    monkeypatch.setenv(
        "profile2" + "_" + environment_variables.AWS_SECRET_ACCESS_KEY,
        "my_secret_key",
    )
    monkeypatch.setenv(
        "profile2" + "_" + environment_variables.AWS_DEFAULT_REGION,
        "us-west-2",
    )
    monkeypatch.setenv(
        "profile2" + "_" + environment_variables.AWS_S3_BUCKET,
        "my_bucket",
    )
    monkeypatch.setenv("profile2" + "_" + environment_variables.S3_MOCK, "True")
    with mock_s3():
        # create a mock S3 client
        s3_client = boto3.client("s3")
        # create a mock S3 bucket
        s3_client.create_bucket(Bucket="my_bucket")
        # upload the payload to the bucket
        store = CCStoreS3()
        store.set_payload(payload)
        data1_input = PutObjectInput(
            file_name="data1",
            file_extension="",
            dest_store_type=StoreType.S3,
            object_state=ObjectState.MEMORY,
            data=b"test data 1",
            source_root_path="",
            dest_root_path="store1_root/path/to",
        )
        data2_input = PutObjectInput(
            file_name="data2",
            file_extension="",
            dest_store_type=StoreType.S3,
            object_state=ObjectState.MEMORY,
            data=b"test data 2",
            source_root_path="",
            dest_root_path="store2_root/path/to",
        )
        store.put_object(data1_input)
        store.put_object(data2_input)
        yield PluginManager()
        # cleanup mock s3 bucket
        response = s3_client.list_objects_v2(Bucket="my_bucket")
        if "Contents" in response:
            delete_keys = [{"Key": obj["Key"]} for obj in response["Contents"]]
            s3_client.delete_objects(
                Bucket="my_bucket", Delete={"Objects": delete_keys}
            )
        s3_client.delete_bucket(Bucket="my_bucket")


def test_get_payload(plugin_manager, payload):
    os.environ["TEST_ENV_VAR"] = "test"
    test_payload = plugin_manager.get_payload()
    assert test_payload.attributes == payload.attributes
    assert test_payload.outputs == payload.outputs
    assert test_payload.inputs[1] == payload.inputs[1]
    # make sure path was substitited
    assert test_payload.inputs[0].data_paths[0] == "test/path/to/value1"


def test_get_file_store(plugin_manager):
    assert isinstance(plugin_manager.get_file_store("store1"), FileDataStoreS3)


def test_get_store(plugin_manager):
    assert plugin_manager.get_store("store2").name == "store2"


def test_get_input_data_source(plugin_manager):
    assert plugin_manager.get_input_data_source("input1").name == "input1"


def test_get_output_data_source(plugin_manager):
    assert plugin_manager.get_output_data_source("output1").name == "output1"


def test_get_input_data_sources(plugin_manager):
    assert plugin_manager.get_input_data_sources()[0].name == "input1"


def test_get_output_data_sources(plugin_manager):
    assert plugin_manager.get_output_data_sources()[0].name == "output1"


def test_get_file(plugin_manager):
    data_source = plugin_manager.get_input_data_source("input1")
    assert plugin_manager.get_file(data_source, 0) == b"test data 1"
    assert plugin_manager.get_file(data_source, 1) is None


def test_put_file(plugin_manager):
    data_source = plugin_manager.get_output_data_source("output1")
    assert plugin_manager.put_file(b"output data 1", data_source, 0) is True


def test_file_writer(plugin_manager):
    data_source = plugin_manager.get_output_data_source("output2")
    assert (
        plugin_manager.file_writer(io.BytesIO(b"output data 2"), data_source, 0) is True
    )


def test_file_reader(plugin_manager):
    data_source = plugin_manager.get_output_data_source("output2")
    plugin_manager.file_writer(io.BytesIO(b"output data 2"), data_source, 0)
    assert plugin_manager.file_reader(data_source, 0).getvalue() == b"output data 2"


def test_file_reader_by_name(plugin_manager):
    data_source = plugin_manager.get_input_data_source("input1")
    plugin_manager.file_writer(io.BytesIO(b"input data 1"), data_source, 0)
    assert plugin_manager.file_reader_by_name("input1", 0).getvalue() == b"input data 1"


def test_event_number(plugin_manager):
    assert isinstance(plugin_manager.event_number(), int)


def test_find_data_source(plugin_manager):
    assert (
        plugin_manager._find_data_source(
            "input1", plugin_manager.get_input_data_sources()
        ).name
        == "input1"
    )


def test_find_data_store(plugin_manager):
    assert plugin_manager._find_data_store("store1").name == "store1"


def test_unimplemented_store_types(monkeypatch):
    # CCStore Env vars
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
    monkeypatch.setenv(environment_variables.CC_MANIFEST_ID, "my_manifest")
    monkeypatch.setenv(environment_variables.CC_ROOT, "my_root")
    monkeypatch.setenv(
        environment_variables.CC_PROFILE + "_" + environment_variables.S3_MOCK, "True"
    )
    ## plugin env vars
    monkeypatch.setenv(environment_variables.CC_PLUGIN_DEFINITION, "test_plugin")
    monkeypatch.setenv(
        environment_variables.CC_EVENT_NUMBER,
        "000",
    )
    ## profile1 env vars
    monkeypatch.setenv(
        "profile1" + "_" + environment_variables.AWS_ACCESS_KEY_ID,
        "my_access_key",
    )
    monkeypatch.setenv(
        "profile1" + "_" + environment_variables.AWS_SECRET_ACCESS_KEY,
        "my_secret_key",
    )
    monkeypatch.setenv(
        "profile1" + "_" + environment_variables.AWS_DEFAULT_REGION,
        "us-west-2",
    )
    monkeypatch.setenv(
        "profile1" + "_" + environment_variables.AWS_S3_BUCKET,
        "my_bucket",
    )
    monkeypatch.setenv("profile1" + "_" + environment_variables.S3_MOCK, "True")
    ## profile2 env vars
    monkeypatch.setenv(
        "profile2" + "_" + environment_variables.AWS_ACCESS_KEY_ID,
        "my_access_key",
    )
    monkeypatch.setenv(
        "profile2" + "_" + environment_variables.AWS_SECRET_ACCESS_KEY,
        "my_secret_key",
    )
    monkeypatch.setenv(
        "profile2" + "_" + environment_variables.AWS_DEFAULT_REGION,
        "us-west-2",
    )
    monkeypatch.setenv(
        "profile2" + "_" + environment_variables.AWS_S3_BUCKET,
        "my_bucket",
    )
    monkeypatch.setenv("profile2" + "_" + environment_variables.S3_MOCK, "True")
    with mock_s3():
        # create a mock S3 client
        s3_client = boto3.client("s3")
        # create a mock S3 bucket
        s3_client.create_bucket(Bucket="my_bucket")
        # upload the payload to the bucket
        store = CCStoreS3()
        # test WS store payload
        store.set_payload(
            Payload(
                attributes={},
                stores=[
                    DataStore(
                        name="store1",
                        id="store_id1",
                        parameters={"param1": "value1", "root": "store1_root"},
                        store_type=StoreType.WS,
                        ds_profile="profile1",
                    )
                ],
                inputs=[],
                outputs=[],
            )
        )
        # pylint: disable=protected-access
        PluginManager._instance = (
            None  # don't do this in real code, it defeats the purpose of a singleton.
        )
        with pytest.raises(NotImplementedError):
            PluginManager()
        # pylint: disable=protected-access
        PluginManager._instance = (
            None  # don't do this in real code, it defeats the purpose of a singleton.
        )
        # test RDBMS store payload
        store.set_payload(
            Payload(
                attributes={},
                stores=[
                    DataStore(
                        name="store1",
                        id="store_id1",
                        parameters={"param1": "value1", "root": "store1_root"},
                        store_type=StoreType.RDBMS,
                        ds_profile="profile1",
                    )
                ],
                inputs=[],
                outputs=[],
            )
        )
        with pytest.raises(NotImplementedError):
            PluginManager()
        # pylint: disable=protected-access
        PluginManager._instance = (
            None  # don't do this in real code, it defeats the purpose of a singleton.
        )
        # test EBS store payload
        store.set_payload(
            Payload(
                attributes={},
                stores=[
                    DataStore(
                        name="store1",
                        id="store_id1",
                        parameters={"param1": "value1", "root": "store1_root"},
                        store_type=StoreType.EBS,
                        ds_profile="profile1",
                    )
                ],
                inputs=[],
                outputs=[],
            )
        )
        with pytest.raises(NotImplementedError):
            PluginManager()
        # pylint: disable=protected-access
        PluginManager._instance = (
            None  # don't do this in real code, it defeats the purpose of a singleton.
        )
        # cleanup mock s3 bucket
        response = s3_client.list_objects_v2(Bucket="my_bucket")
        if "Contents" in response:
            delete_keys = [{"Key": obj["Key"]} for obj in response["Contents"]]
            s3_client.delete_objects(
                Bucket="my_bucket", Delete={"Objects": delete_keys}
            )
        s3_client.delete_bucket(Bucket="my_bucket")

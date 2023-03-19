import boto3
from botocore.exceptions import ClientError
from .cc_store import CCStore
from .get_object_input import GetObjectInput
from .pull_object_input import PullObjectInput
from .put_object_input import PutObjectInput
from .payload import Payload
from .store_type import StoreType
from . import environment_variables
from .aws_config import AWSConfig
from . import constants
from botocore.client import Config
from .object_state import ObjectState
import io
import os
import boto3


class CCStoreS3(CCStore):
    """An implementation of the abstract CCStore class for use with AWS S3 as the data store.
    You must set the following required and options environment variables to construct an object of this class:

    Required:
    - CC_AWS_ACCESS_KEY_ID: AWS credentials
    - CC_AWS_SECRET_ACCESS_KEY: AWS credentials
    - CC_AWS_DEFAULT_REGION: the region the bucket is in
    - CC_AWS_S3_BUCKET: the bucket name to use
    - CC_S3_ENDPOINT: the AWS S3 endpoint for the bucket
    - CC_EVENT_NUMBER: CC event number to use
    - CC_ROOT: The root prefix on S3 where the payload will be stored in s3://<CC_AWS_S3_BUCKET>/<CC_ROOT>/<CC_EVENT_NUMBER>/payload

    Optional:
    - CC_S3_MOCK: True or False. If true, bucket will be mocked
    - CC_S3_DISABLE_SSL: True or False. If true, bucket will not use SSL
    - CC_S3_FORCE_PATH_STYLE: True or False. If true, bucket will force path style
    """

    def __init__(self):
        self.local_root_path = ""
        self.bucket = ""
        self.root = ""
        self.manifest_id = ""
        self.store_type = StoreType.S3
        self.aws_s3 = None
        self.config = AWSConfig()
        self._initialize()

    def _initialize(self):
        """Initalizes the class using environment variables

        Raises:
            EnvironmentError: if a required env variable is not set
        """
        required_env_vars = {
            "aws_access_key_id_env_key": environment_variables.CC_PROFILE
            + "_"
            + environment_variables.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key_id_env_key": environment_variables.CC_PROFILE
            + "_"
            + environment_variables.AWS_SECRET_ACCESS_KEY,
            "aws_region_env_key": environment_variables.CC_PROFILE
            + "_"
            + environment_variables.AWS_DEFAULT_REGION,
            "aws_bucket_env_key": environment_variables.CC_PROFILE
            + "_"
            + environment_variables.AWS_S3_BUCKET,
            "aws_endpoint_env_key": environment_variables.CC_PROFILE
            + "_"
            + environment_variables.S3_ENDPOINT,
            "manifest_id_env_key": environment_variables.CC_MANIFEST_ID,
            "cc_root_env_key": environment_variables.CC_ROOT,
        }
        for _, value in required_env_vars.items():
            if value not in os.environ:
                raise EnvironmentError(f"{value} environment variable not set")

        aws_access_key_id = str(
            os.getenv(required_env_vars["aws_access_key_id_env_key"])
        )
        aws_secret_access_key_id = str(
            os.getenv(required_env_vars["aws_secret_access_key_id_env_key"])
        )
        # automatically convert to standard format e.g. "us-east-1"
        aws_region = (
            str(os.getenv(required_env_vars["aws_region_env_key"]))
            .lower()
            .replace("_", "-")
        )
        aws_bucket = str(os.getenv(required_env_vars["aws_bucket_env_key"]))
        aws_endpoint = str(os.getenv(required_env_vars["aws_endpoint_env_key"]))

        optional_env_vars = {
            "aws_mock_env_key": environment_variables.CC_PROFILE
            + "_"
            + environment_variables.S3_MOCK,
            "aws_disable_ssl_env_key": environment_variables.CC_PROFILE
            + "_"
            + environment_variables.S3_DISABLE_SSL,
            "aws_force_path_style_env_key": environment_variables.CC_PROFILE
            + "_"
            + environment_variables.S3_FORCE_PATH_STYLE,
        }

        aws_mock = bool(os.getenv(optional_env_vars["aws_mock_env_key"]))
        aws_disable_ssl = bool(os.getenv(optional_env_vars["aws_disable_ssl_env_key"]))
        aws_force_path_style = bool(
            os.getenv(optional_env_vars["aws_force_path_style_env_key"])
        )

        acfg = AWSConfig(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key_id=aws_secret_access_key_id,
            aws_region=aws_region,
            aws_bucket=aws_bucket,
            aws_endpoint=aws_endpoint,
            aws_mock=aws_mock,
            aws_disable_ssl=aws_disable_ssl,
            aws_force_path_style=aws_force_path_style,
        )
        self.config = acfg

        self.aws_s3 = self.create_s3_client(self.config)

        self.store_type = StoreType.S3
        self.manifest_id = str(os.getenv(required_env_vars["manifest_id_env_key"]))
        self.local_root_path = constants.LOCAL_ROOT_PATH
        self.bucket = self.config.aws_bucket
        self.root = str(os.getenv(required_env_vars["cc_root_env_key"]))

    @staticmethod
    def create_s3_client(config: AWSConfig):
        """Initalize the S3 client using the config settings. When mocked, all config settings are ignored

        Args:
            config (AWSConfig): the config settings used to create the s3 client

        Returns:
            The boto3 AWS S3 Client object
        """
        if config.aws_mock:
            return boto3.client("s3")
        if config.aws_force_path_style:
            client_config = Config(
                signature_version="s3v4", s3={"addressing_style": "path"}
            )
        else:
            client_config = Config(signature_version="s3v4")
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key_id,
            region_name=config.aws_region,
            endpoint_url=config.aws_endpoint,
            use_ssl=not config.aws_disable_ssl,
            verify=not config.aws_disable_ssl,
            config=client_config,
        )
        return s3_client

    def handles_data_store_type(self, data_store_type: StoreType) -> bool:
        return self.store_type == data_store_type

    def put_object(self, input: PutObjectInput) -> bool:
        """Put an object on S3. Object can be in memory or on disk.

        Args:
            input (PutObjectInput): inputs

        Raises:
            FileNotFoundError: given file does not exist on disk
            IOError: error reading file from disk

        Returns:
            bool: True is put is successful
        """
        match input.object_state:
            case ObjectState.LocalDisk:
                # read from local
                try:
                    with open(input.source_path, "rb") as f:
                        data = f.read()
                        self.upload_to_s3(input.dest_path, data)
                except FileNotFoundError:
                    # TODO
                    raise FileNotFoundError
                except IOError:
                    # TODO
                    raise IOError
                return True

            case ObjectState.Memory:
                self.upload_to_s3(input.dest_path, input.data)
                return True
            case _:
                return False

    def pull_object(self, input: PullObjectInput) -> bool:
        """Pull an object from S3 to a local file path

        Args:
            input (PullObjectInput): inputs

        Returns:
            bool: True is pull is successful
        """
        remote_path = input.source_root_path + "/" + input.file_name
        local_path = input.dest_root_path + "/" + input.file_name
        if len(input.file_extension) > 0:
            remote_path += "." + input.file_extension
            local_path += "." + input.file_extension
        try:
            data = self.download_bytes_from_s3(remote_path)
            self.write_input_stream_to_disk(io.BytesIO(data), local_path)
        except Exception:
            return False
        return True

    def get_object(self, input: GetObjectInput) -> bytes:
        """Get an object from S3 to memory

        Args:
            input (GetObjectInput): inputs

        Returns:
            bytes: data from the get request
        """
        remote_path = input.source_root_path + "/" + input.file_name
        if len(input.file_extension) > 0:
            remote_path += "." + input.file_extension
        try:
            return self.download_bytes_from_s3(remote_path)
        except ClientError as e:
            raise Exception(str(e))

    def get_payload(self) -> Payload:
        """Get the payload from S3. The payload is always at:
            s3://<CC_AWS_S3_BUCKET>/<CC_ROOT>/<CC_EVENT_NUMBER>/payload

        Returns:
            Payload: the payload object
        """
        path = self.root + "/" + self.manifest_id + "/" + constants.PAYLOAD_FILE_NAME
        try:
            body = self.download_bytes_from_s3(path)
            return self.read_json_model_payload_from_bytes(body)
        except ClientError as e:
            raise Exception(str(e))

    @staticmethod
    def read_json_model_payload_from_bytes(data: bytes) -> Payload:
        """Helper method to decode the JSON to a Payload object"""
        try:
            return Payload.from_json(data.decode("utf-8"))
        except Exception as e:
            raise e

    def write_input_stream_to_disk(
        self, input_stream: io.BytesIO, output_destination: str
    ) -> None:
        directory = os.path.dirname(output_destination)
        if not os.path.exists(directory):
            os.makedirs(directory)
        bytes_data = input_stream.read()
        with open(output_destination, "wb") as output_file:
            output_file.write(bytes_data)

    def upload_to_s3(self, object_key: str, file_bytes: bytes) -> None:
        if self.aws_s3 is not None:
            self.aws_s3.put_object(Bucket=self.bucket, Key=object_key, Body=file_bytes)
        else:
            raise RuntimeError("AWS config not set.")

    def download_bytes_from_s3(self, object_key: str) -> bytes:
        if self.aws_s3 is not None:
            response = self.aws_s3.get_object(Bucket=self.bucket, Key=object_key)
            file_bytes = response["Body"].read()
            return file_bytes
        else:
            raise RuntimeError("AWS config not set.")

    def root_path(self) -> str:
        return self.bucket

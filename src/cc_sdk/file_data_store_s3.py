import io
import os
from .file_data_store import FileDataStore
from .store_type import StoreType
from .aws_config import AWSConfig
from .data_store import DataStore
from .cc_store_s3 import CCStoreS3


class FileDataStoreS3(FileDataStore):
    S3_ROOT = "root"

    def __init__(self, data_store: DataStore):
        self.bucket = ""
        self.post_fix = ""
        self.store_type = StoreType.S3
        self.aws_s3 = None
        self.config = AWSConfig
        self._initialize(data_store)

    def _initialize(self, data_store: DataStore):
        """Initalizes the class using environment variables

        Raises:
            EnvironmentError: if a required env variable is not set
        """
        self.config = CCStoreS3.create_aws_config_from_env(
            env_prefix=data_store.ds_profile
        )

        self.aws_s3 = CCStoreS3.create_s3_client(self.config)

        self.store_type = StoreType.S3
        self.bucket = self.config.aws_bucket
        try:
            # TODO post_fix is used as a prefix, should we rename?
            self.post_fix = data_store.parameters[self.S3_ROOT]
        except KeyError:
            # TODO, throw error?
            print("Missing S3 Root Paramter. Cannot create the store.")

    def _get_object(self, path: str):
        """Alias for _download_bytes_from_s3"""
        return self._download_bytes_from_s3(path)

    def _download_bytes_from_s3(self, object_key: str) -> bytes:
        # standard file separators, replace \ with /
        key = os.path.join(self.post_fix, object_key).replace("\\", "/")
        if self.aws_s3 is not None:
            response = self.aws_s3.get_object(Bucket=self.bucket, Key=key)
            file_bytes = response["Body"].read()
            return file_bytes
        raise RuntimeError("AWS config not set.")

    def _upload_to_s3(self, object_key: str, file_bytes: bytes) -> bool:
        if self.aws_s3 is not None:
            self.aws_s3.put_object(Bucket=self.bucket, Key=object_key, Body=file_bytes)
            return True
        return False

    def copy(self, dest_store: FileDataStore, src_path: str, dest_path: str) -> bool:
        data = self._get_object(src_path)
        return dest_store.put(io.BytesIO(data), dest_path)

    def get(self, path: str) -> io.BytesIO:
        return io.BytesIO(self._get_object(path))

    def put(self, data: io.BytesIO, path: str) -> bool:
        return self._upload_to_s3(self.post_fix + "/" + path, data.getvalue())

    def delete(self, path: str) -> bool:
        # standard file separators, replace \ with /
        key = os.path.join(self.post_fix, path).replace("\\", "/")
        if self.aws_s3 is not None:
            self.aws_s3.delete_object(Bucket=self.bucket, Key=key)
            return True
        return False

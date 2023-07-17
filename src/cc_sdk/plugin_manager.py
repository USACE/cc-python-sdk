import re
import os
import io
from botocore.exceptions import ClientError
from .cc_store_s3 import CCStoreS3
from .payload import Payload
from .logger import Logger
from .error import ErrorLevel
from .store_type import StoreType
from .file_data_store_s3 import FileDataStoreS3
from .file_data_store import FileDataStore
from . import environment_variables
from .data_store import DataStore
from .data_source import DataSource
from .message import Message
from .error import Error
from .status import Status


class PluginManager:
    """
    The PluginManager class manages plugins and their associated data sources and data stores. It loads and processes
    a payload that defines the input and output data sources and data stores to be used by a plugin. It also provides
    methods to retrieve files from and store files in the data stores.


    Methods:
        get_payload(cls) -> Payload:
        Returns the payload object associated with the current plugin.

        get_file_store(cls, store_name: str) -> FileDataStore:
        Finds the data store with the given name and returns its file data store session object.

        get_store(cls, store_name: str) -> DataStore:
        Finds the data store with the given name and returns the data store object.

        get_input_data_source(cls, name: str) -> DataSource:
        Finds the input data source with the given name and returns its data source object.

        get_output_data_source(cls, name: str) -> DataSource:
        Finds the output data source with the given name and returns its data source object.

        get_input_data_sources(cls) -> list[DataSource]:
        Returns a list of all input data sources in the payload.

        get_output_data_sources(cls) -> list[DataSource]:
        Returns a list of all output data sources in the payload.

        get_file(cls, data_source: DataSource, path_index: int) -> bytes | None:
        Returns the content of a file associated with the specified data source and path index.

        put_file(cls, data: bytes, data_source: DataSource, path_index: int) -> bool:
        Stores the given data in the file associated with the specified data source and path index.

        file_writer(cls, input_stream: io.BytesIO, dest_data_source: DataSource, dest_path_index: int) -> bool:
        Stores data from the given input stream in the file associated with the specified data source and path index.

        file_reader(cls, data_source: DataSource, path_index: int) -> io.BytesIO:
        Returns a stream object that can be used to read the contents of the file associated with the specified data
        source and path index.

        file_reader_by_name(cls, data_source_name: str, path_index: int) -> io.BytesIO:
        Returns a stream object that can be used to read the contents of the file associated with the data source with
        the specified name and path index.

        set_log_level(cls, level: ErrorLevel) -> None:
        Sets the logging level for the current instance.

        log_message(cls, message: Message) -> None:
        Logs the given message object.

        log_error(cls, error: Error) -> None:
        Logs the given error object.

        report_progress(cls, report: Status) -> None:
        Logs a progress report.

        event_number(cls) -> int:
        Returns the event number associated with the current instance.
    """

    _instance = None  # the instance of this singleton class
    _has_updated_paths = False  # have the paths been updated? this happens the first time the payload is requested with get_payload()

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._init()
        return cls._instance

    @classmethod
    def _init(cls):
        cls._pattern = re.compile(
            r"(?<=\{).+?(?=\})"
        )  # matchs first string inside curly braces
        sender = os.getenv(environment_variables.CC_PLUGIN_DEFINITION)
        if sender is None:
            raise EnvironmentError(
                f"{environment_variables.CC_PLUGIN_DEFINITION} environment variable not set"
            )
        cls._logger = Logger(ErrorLevel.DEBUG, sender)
        cls._cc_store = CCStoreS3()
        try:
            cls._payload: Payload = cls._cc_store.get_payload()
            # pylint can't determine stores type
            # pylint: disable=not-an-iterable
            for store in cls._payload.stores:
                match store.store_type:
                    case StoreType.S3:
                        # store is a reference so this updates the payload object
                        store.session = FileDataStoreS3(store)
                    case StoreType.WS:
                        # TODO
                        raise NotImplementedError(
                            "Payload StoreType 'WS' not implemented"
                        )
                    case StoreType.RDBMS:
                        # TODO
                        raise NotImplementedError(
                            "Payload StoreType 'RDBMS' not implemented"
                        )
                    case StoreType.EBS:
                        # TODO
                        raise NotImplementedError(
                            "Payload StoreType 'EBS' not implemented"
                        )
                    case _:
                        raise RuntimeError("Payload contains invalid StoreType.")
        except EnvironmentError as exc:
            raise exc
        except NotImplementedError as exc:
            raise exc
        except Exception as exc:
            raise RuntimeError(
                f"Could not acquire payload file. ERROR: {str(exc)}"
            ) from exc

    @classmethod
    def _substitute_path_variables(cls) -> None:
        """
        Substitute placeholders in all input and output paths of the payload.

        For each input and output path in the payload, this function calls the
        `_substitute_data_source_path` method to substitute any placeholders
        found in the path with their corresponding values.

        This function modifies the input and output paths in-place.

        Returns:
            None
        """
        # pylint can't determine types from Payload
        # pylint: disable=unsubscriptable-object
        for i, _ in enumerate(cls._payload.inputs):
            existing_data_source = cls._payload.inputs[i]
            updated_data_source = DataSource(
                name=cls.substitute_paths(existing_data_source.name),
                id=existing_data_source.id,
                store_name=existing_data_source.store_name,
                paths=[
                    cls.substitute_paths(path) for path in existing_data_source.paths
                ],
                data_paths=[
                    cls.substitute_paths(path)
                    for path in existing_data_source.data_paths
                ],
            )
            cls._payload.inputs[i] = updated_data_source
        for i, _ in enumerate(cls._payload.outputs):
            existing_data_source = cls._payload.outputs[i]
            updated_data_source = DataSource(
                name=cls.substitute_paths(existing_data_source.name),
                id=existing_data_source.id,
                store_name=existing_data_source.store_name,
                paths=[
                    cls.substitute_paths(path) for path in existing_data_source.paths
                ],
                data_paths=[
                    cls.substitute_paths(path)
                    for path in existing_data_source.data_paths
                ],
            )
            cls._payload.outputs[i] = updated_data_source
        # TODO: substitute paths for actions once they are implemented

    @classmethod
    def substitute_paths(cls, path) -> str:
        """
        Substitute placeholders in a data source path with their corresponding values.

        Args:
            path (str): A string containing placeholders to substitute.

        Returns:
            str: The `path` string with all placeholders substituted with their values.

        Raises:
            RuntimeError: If a placeholder refers to a missing attribute in the payload's `attributes` dictionary.
        """
        the_match = cls._pattern.search(path)
        while the_match:
            result = the_match.group()
            parts = result.split("::", 1)
            prefix = parts[0]
            if prefix == "ENV":
                val = os.getenv(parts[1])
                if val is None:
                    raise EnvironmentError(f"Environment variable {parts[1]} is not set but required for path '{path}'")
                path = path.replace("{" + result + "}", val)
            elif prefix == "ATTR":
                try:
                    # pylint can't determine attributes type
                    # pylint: disable=unsubscriptable-object
                    valattr = str(cls._payload.attributes[parts[1]])
                    path = path.replace("{" + result + "}", valattr)
                except KeyError as exc:
                    raise RuntimeError(
                        f"Payload attributes has no key {parts[1]}."
                    ) from exc
            the_match = cls._pattern.search(path)
        return path

    @classmethod
    def get_payload(cls) -> Payload:
        if not cls._has_updated_paths:
            cls._substitute_path_variables()
            cls._has_updated_paths = True
        return cls._payload

    @classmethod
    def get_file_store(cls, store_name: str) -> FileDataStore:
        data_store = cls._find_data_store(store_name)
        if data_store is None:
            raise RuntimeError(f"DataStore with name '{store_name}' was not found.")
        if isinstance(data_store.session, FileDataStore):
            return data_store.session
        raise RuntimeError("DataStore session object is invalid.")

    @classmethod
    def get_store(cls, store_name: str) -> DataStore:
        data_store = cls._find_data_store(store_name)
        if data_store is None:
            raise RuntimeError(f"DataStore with name '{store_name}' was not found")
        return data_store

    @classmethod
    def get_input_data_source(cls, name: str) -> DataSource:
        data_source = cls._find_data_source(name, cls.get_input_data_sources())
        if data_source is None:
            raise RuntimeError(f"Input DataSource with name '{name}' was not found")
        return data_source

    @classmethod
    def get_output_data_source(cls, name: str) -> DataSource:
        data_source = cls._find_data_source(name, cls.get_output_data_sources())
        if data_source is None:
            raise RuntimeError(f"Output DataSource with name '{name}' was not found")
        return data_source

    @classmethod
    def get_input_data_sources(cls) -> list[DataSource]:
        return cls._payload.inputs

    @classmethod
    def get_output_data_sources(cls) -> list[DataSource]:
        return cls._payload.outputs

    @classmethod
    def get_file(cls, data_source: DataSource, path_index: int) -> bytes | None:
        store = cls.get_file_store(data_source.store_name)
        try:
            reader = store.get(data_source.paths[path_index])
            data = reader.getvalue()
            return data
        except ClientError:
            return None
        except IndexError:
            return None

    @classmethod
    def put_file(cls, data: bytes, data_source: DataSource, path_index: int) -> bool:
        store = cls.get_file_store(data_source.store_name)
        return store.put(io.BytesIO(data), data_source.paths[path_index])

    @classmethod
    def file_writer(
        cls,
        input_stream: io.BytesIO,
        dest_data_source: DataSource,
        dest_path_index: int,
    ) -> bool:
        store = cls.get_file_store(dest_data_source.store_name)
        return store.put(input_stream, dest_data_source.paths[dest_path_index])

    @classmethod
    def file_reader(cls, data_source: DataSource, path_index: int) -> io.BytesIO:
        store = cls.get_file_store(data_source.store_name)
        return store.get(data_source.paths[path_index])

    @classmethod
    def file_reader_by_name(cls, data_source_name: str, path_index: int) -> io.BytesIO:
        data_source = cls._find_data_source(
            data_source_name, cls.get_input_data_sources()
        )
        if data_source is None:
            raise RuntimeError(
                f"Input DataSource with name: '{data_source_name}' not found."
            )
        return cls.file_reader(data_source, path_index)

    @classmethod
    def set_log_level(cls, level: ErrorLevel) -> None:
        cls._logger.set_error_level(level)

    @classmethod
    def log_message(cls, message: Message) -> None:
        cls._logger.log_message(message)

    @classmethod
    def log_error(cls, error: Error) -> None:
        cls._logger.log_error(error)

    @classmethod
    def report_progress(cls, report: Status) -> None:
        cls._logger.report_status(report)

    @classmethod
    def event_number(cls) -> int:
        val = os.getenv(environment_variables.CC_EVENT_NUMBER)
        if val is None:
            raise EnvironmentError(
                f"{environment_variables.CC_EVENT_NUMBER} environment variable not set"
            )
        event_number = int(val)
        return event_number

    @classmethod
    def _find_data_source(
        cls, name: str, data_sources: list[DataSource]
    ) -> DataSource | None:
        for data_source in data_sources:
            if data_source.name.lower() == name.lower():
                return data_source
        return None

    @classmethod
    def _find_data_store(cls, name: str) -> DataStore | None:
        # pylint can't determine attributes type
        # pylint: disable=not-an-iterable
        for data_store in cls._payload.stores:
            if data_store.name.lower() == name.lower():
                return data_store
        return None

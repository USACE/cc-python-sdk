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
        get_payload(self) -> Payload:
        Returns the payload object associated with the current plugin.

        get_file_store(self, store_name: str) -> FileDataStore:
        Finds the data store with the given name and returns its file data store session object.

        get_store(self, store_name: str) -> DataStore:
        Finds the data store with the given name and returns the data store object.

        get_input_data_source(self, name: str) -> DataSource:
        Finds the input data source with the given name and returns its data source object.

        get_output_data_source(self, name: str) -> DataSource:
        Finds the output data source with the given name and returns its data source object.

        get_input_data_sources(self) -> list[DataSource]:
        Returns a list of all input data sources in the payload.

        get_output_data_sources(self) -> list[DataSource]:
        Returns a list of all output data sources in the payload.

        get_file(self, data_source: DataSource, path_index: int) -> bytes | None:
        Returns the content of a file associated with the specified data source and path index.

        put_file(self, data: bytes, data_source: DataSource, path_index: int) -> bool:
        Stores the given data in the file associated with the specified data source and path index.

        file_writer(self, input_stream: io.BytesIO, dest_data_source: DataSource, dest_path_index: int) -> bool:
        Stores data from the given input stream in the file associated with the specified data source and path index.

        file_reader(self, data_source: DataSource, path_index: int) -> io.BytesIO:
        Returns a stream object that can be used to read the contents of the file associated with the specified data
        source and path index.

        file_reader_by_name(self, data_source_name: str, path_index: int) -> io.BytesIO:
        Returns a stream object that can be used to read the contents of the file associated with the data source with
        the specified name and path index.

        set_log_level(self, level: ErrorLevel) -> None:
        Sets the logging level for the current instance.

        log_message(self, message: Message) -> None:
        Logs the given message object.

        log_error(self, error: Error) -> None:
        Logs the given error object.

        report_progress(self, report: Status) -> None:
        Logs a progress report.

        event_number(self) -> int:
        Returns the event number associated with the current instance.
    """

    def __init__(self):
        self._pattern = re.compile(r"(?<=\{).+?(?=\})")
        sender = os.getenv(environment_variables.CC_PLUGIN_DEFINITION)
        if sender is None:
            raise EnvironmentError(
                f"{environment_variables.CC_PLUGIN_DEFINITION} environment variable not set"
            )
        self._logger = Logger(ErrorLevel.DEBUG, sender)
        self._cc_store = CCStoreS3()
        try:
            self._payload: Payload = self._cc_store.get_payload()
            # pylint can't determine stores type
            # pylint: disable=not-an-iterable
            for store in self._payload.stores:
                match store.store_type:
                    case StoreType.S3:
                        # store is a reference so this updates the payload object
                        store.session = FileDataStoreS3(store)
                    case StoreType.WS:
                        # TODO
                        raise NotImplementedError("Payload StoreType 'WS' not implemented")
                    case StoreType.RDBMS:
                        # TODO
                        raise NotImplementedError("Payload StoreType 'RDBMS' not implemented")
                    case StoreType.EBS:
                        # TODO
                        raise NotImplementedError("Payload StoreType 'EBS' not implemented")
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

    def _substitute_path_variables(self) -> None:
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
        for i, input_obj in enumerate(self._payload.inputs):
            for j, path in enumerate(input_obj.paths):
                self._payload.inputs[i].paths[j] = self._substitute_data_source_path(
                    path
                )

        for i, output_obj in enumerate(self._payload.outputs):
            for j, path in enumerate(output_obj.paths):
                self._payload.outputs[i].paths[j] = self._substitute_data_source_path(
                    path
                )

    def _substitute_data_source_path(self, path) -> str:
        """
        Substitute placeholders in a data source path with their corresponding values.

        Args:
            path (str): A string containing placeholders to substitute.

        Returns:
            str: The `path` string with all placeholders substituted with their values.

        Raises:
            RuntimeError: If a placeholder refers to a missing attribute in the payload's `attributes` dictionary.
        """
        the_match = self._pattern.search(path)
        while the_match:
            result = the_match.group()
            parts = result.split("::", 1)
            prefix = parts[0]
            if prefix == "ENV":
                val = os.getenv(parts[1])
                path = path.replace(result, val)
            elif prefix == "ATTR":
                try:
                    # pylint can't determine attributes type
                    # pylint: disable=unsubscriptable-object
                    valattr = str(self._payload.attributes[parts[1]])
                    path = path.replace(result, valattr)
                except KeyError as exc:
                    raise RuntimeError(
                        f"Payload attributes has no key {parts[1]}."
                    ) from exc
            the_match = self._pattern.search(path)
        return path

    def get_payload(self) -> Payload:
        return self._payload

    def get_file_store(self, store_name: str) -> FileDataStore:
        data_store = self._find_data_store(store_name)
        if data_store is None:
            raise RuntimeError(f"DataStore with name '{store_name}' was not found.")
        if isinstance(data_store.session, FileDataStore):
            return data_store.session
        raise RuntimeError("DataStore session object is invalid.")

    def get_store(self, store_name: str) -> DataStore:
        data_store = self._find_data_store(store_name)
        if data_store is None:
            raise RuntimeError(f"DataStore with name '{store_name}' was not found")
        return data_store

    def get_input_data_source(self, name: str) -> DataSource:
        data_source = self._find_data_source(name, self.get_input_data_sources())
        if data_source is None:
            raise RuntimeError(f"Input DataSource with name '{name}' was not found")
        return data_source

    def get_output_data_source(self, name: str) -> DataSource:
        data_source = self._find_data_source(name, self.get_output_data_sources())
        if data_source is None:
            raise RuntimeError(f"Output DataSource with name '{name}' was not found")
        return data_source

    def get_input_data_sources(self) -> list[DataSource]:
        return self._payload.inputs

    def get_output_data_sources(self) -> list[DataSource]:
        return self._payload.outputs

    def get_file(self, data_source: DataSource, path_index: int) -> bytes | None:
        store = self.get_file_store(data_source.store_name)
        try:
            reader = store.get(data_source.paths[path_index])
            data = reader.getvalue()
            return data
        except ClientError:
            return None
        except IndexError:
            return None

    def put_file(self, data: bytes, data_source: DataSource, path_index: int) -> bool:
        store = self.get_file_store(data_source.store_name)
        return store.put(io.BytesIO(data), data_source.paths[path_index])

    def file_writer(
        self,
        input_stream: io.BytesIO,
        dest_data_source: DataSource,
        dest_path_index: int,
    ) -> bool:
        store = self.get_file_store(dest_data_source.store_name)
        return store.put(input_stream, dest_data_source.paths[dest_path_index])

    def file_reader(self, data_source: DataSource, path_index: int) -> io.BytesIO:
        store = self.get_file_store(data_source.store_name)
        return store.get(data_source.paths[path_index])

    def file_reader_by_name(self, data_source_name: str, path_index: int) -> io.BytesIO:
        data_source = self._find_data_source(
            data_source_name, self.get_input_data_sources()
        )
        if data_source is None:
            raise RuntimeError(
                f"Input DataSource with name: '{data_source_name}' not found."
            )
        return self.file_reader(data_source, path_index)

    def set_log_level(self, level: ErrorLevel) -> None:
        self._logger.set_error_level(level)

    def log_message(self, message: Message) -> None:
        self._logger.log_message(message)

    def log_error(self, error: Error) -> None:
        self._logger.log_error(error)

    def report_progress(self, report: Status) -> None:
        self._logger.report_status(report)

    def event_number(self) -> int:
        val = os.getenv(environment_variables.CC_EVENT_NUMBER)
        if val is None:
            raise EnvironmentError(
                f"{environment_variables.CC_EVENT_NUMBER} environment variable not set"
            )
        event_number = int(val)
        return event_number

    def _find_data_source(
        self, name: str, data_sources: list[DataSource]
    ) -> DataSource | None:
        for data_source in data_sources:
            if data_source.name.lower() == name.lower():
                return data_source
        return None

    def _find_data_store(self, name: str) -> DataStore | None:
        # pylint can't determine attributes type
        # pylint: disable=not-an-iterable
        for data_store in self._payload.stores:
            if data_store.name.lower() == name.lower():
                return data_store
        return None

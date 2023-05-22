import abc
import io
from typing import Type


class FileDataStore(metaclass=abc.ABCMeta):
    """A base class for implementing a file data store.

    This class defines a set of abstract methods for modifying data in a file
    store. To use this class, you must create a subclass and implement each of
    the abstract methods.

    Attributes:
        None

    Methods:
        - copy(dest_store, src_path, dest_path): copies the specified file from
          this file data store to another, returns true on success and false on
          failure
        - get(path): retrieves a file from the store. Returns a byte stream of
          the file.
        - put(data, path): puts data from a byte stream into a file in the
          store, returns true on success and false on failure
        - delete(path): deletes a file from the store, returns true on success
          and false on failure.
    """

    @abc.abstractmethod
    def copy(
        self, dest_store: Type["FileDataStore"], src_path: str, dest_path: str
    ) -> bool:
        pass

    @abc.abstractmethod
    def get(self, path: str) -> io.BytesIO:
        pass

    @abc.abstractmethod
    def put(self, data: io.BytesIO, path: str) -> bool:
        pass

    @abc.abstractmethod
    def delete(self, path: str) -> bool:
        pass

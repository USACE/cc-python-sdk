from .payload import Payload
import abc


class CCStore(metaclass=abc.ABCMeta):
    """A base class for implementing a data store.

    This class defines a set of abstract methods for storing and retrieving data. To use this class, you must create a
    subclass and implement each of the abstract methods.

    Attributes:
        None

    Methods:
        - put_object(input): stores the given input in the store, returns true on success and false on failure
        - pull_object(input): retrieves the input from the store, returns true on success and false on failure
        - get_object(input): retrieves the object bytes from the store
        - get_payload(): retrieves the payload from the store
        - root_path(): retrieves the root path of the store
        - handles_data_store_type(datastore_type): returns whether the given data store type is handled by this class
    """

    @abc.abstractmethod
    def put_object(self, input) -> bool:
        pass

    @abc.abstractmethod
    def pull_object(self, input) -> bool:
        pass

    @abc.abstractmethod
    def get_object(self, input) -> bytes:
        pass

    @abc.abstractmethod
    def get_payload(self) -> Payload:
        pass

    @abc.abstractmethod
    def root_path(self) -> str:
        pass

    @abc.abstractmethod
    def handles_data_store_type(self, datastore_type) -> bool:
        pass

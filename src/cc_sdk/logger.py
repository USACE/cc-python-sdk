from datetime import date
import sys
from attrs import define, field, validators
from .error import ErrorLevel
from .message import Message
from .error import Error
from .status import Status


@define(auto_attribs=True)
class Logger:
    """
      A class that represents a logger for the sdk.

    Attributes:
    - error_level : ErrorLevel
        The current error level of the logger. private
    - sender : str
        The sender of the current log. private

    Methods:
    - set_error_level(level): sets the current error level for the logger to
      use. Only errors at this level or more severe levels will be reported.
    - log_message(message): logs a message from the sdk. Currenly prints
      to stdout
    - log_error(error): logs an error from the sdk. Currenly prints
      to stderr
    - report_status(report): logs a status object from the sdk. Currenly prints
      to stdout

    Raises:
    - TypeError:
        If the wrong type of object is set for an attribute.
    """

    _error_level: ErrorLevel = field(validator=[validators.instance_of(ErrorLevel)])
    _sender: str = field(validator=[validators.instance_of(str)])

    def set_error_level(self, level: ErrorLevel) -> None:
        self._error_level = level

    def log_message(self, message: Message) -> None:
        today = date.today()
        formatted_date = today.strftime("%Y-%m-%d")
        line = self._sender + ":" + formatted_date + "\n\t" + message.message + "\n"
        sys.stdout.write(line)

    def log_error(self, error: Error) -> None:
        if (
            error.error_level >= self._error_level
            and self._error_level != ErrorLevel.DISABLED
        ):
            today = date.today()
            formatted_date = today.strftime("%Y-%m-%d")
            line = (
                self._sender
                + " issues a "
                + error.error_level.name
                + " error:"
                + formatted_date
                + "\n\t"
                + error.error
                + "\n"
            )
            sys.stderr.write(line)

    def report_status(self, report: Status) -> None:
        today = date.today()
        formatted_date = today.strftime("%Y-%m-%d")
        line = (
            self._sender
            + ":"
            + report.status_level.name
            + ":"
            + formatted_date
            + "\n\t"
            + str(report.progress)
            + " percent complete."
            + "\n"
        )
        sys.stdout.write(line)

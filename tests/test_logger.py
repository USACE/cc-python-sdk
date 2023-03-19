import sys
from datetime import date
from io import StringIO
from cc_sdk.logger import Logger
from cc_sdk.message import Message
from cc_sdk.error import Error, ErrorLevel
from cc_sdk.status import Status, StatusLevel

# pylint: disable=redefined-outer-name


def test_logger_set_error_level():
    # pylint: disable=protected-access
    logger = Logger(ErrorLevel.INFO, "test_sender")
    logger.set_error_level(ErrorLevel.WARN)
    assert logger._error_level == ErrorLevel.WARN


def test_logger_log_message():
    logger = Logger(ErrorLevel.INFO, "test_sender")
    message = Message("test message")
    expected_output = (
        f"test_sender:{date.today().strftime('%Y-%m-%d')}\n\ttest message\n"
    )
    with StringIO() as output:
        sys.stdout = output
        logger.log_message(message)
        assert output.getvalue() == expected_output
    sys.stdout = sys.__stdout__


def test_logger_log_error():
    logger = Logger(ErrorLevel.INFO, "test_sender")
    error = Error("test error", ErrorLevel.ERROR)
    expected_output = f"test_sender issues a ERROR error:{date.today().strftime('%Y-%m-%d')}\n\ttest error\n"
    with StringIO() as output:
        sys.stderr = output
        logger.log_error(error)
        assert output.getvalue() == expected_output
    sys.stderr = sys.__stderr__


def test_logger_report_status():
    logger = Logger(ErrorLevel.INFO, "test_sender")
    status = Status(50, StatusLevel.COMPUTING)
    expected_output = f"test_sender:COMPUTING:{date.today().strftime('%Y-%m-%d')}\n\t50 percent complete.\n"
    with StringIO() as output:
        sys.stdout = output
        logger.report_status(status)
        assert output.getvalue() == expected_output
    sys.stdout = sys.__stdout__

import json
import pytest
from attr.exceptions import FrozenInstanceError
from cc_sdk.error import Error, ErrorLevel

# pylint: disable=redefined-outer-name


@pytest.fixture
def error():
    return Error("test error", ErrorLevel.DEBUG)


def test_getters(error):
    assert error.error == "test error"
    assert error.error_level == ErrorLevel.DEBUG


def test_setters(error):
    with pytest.raises(FrozenInstanceError):
        error.error = "new error"

    with pytest.raises(FrozenInstanceError):
        error.error_level = ErrorLevel.INFO


def test_serialize(error):
    expected_json = json.dumps({"error": "test error", "error_level": "DEBUG"})
    assert expected_json == error.serialize()
    assert json.loads(error.serialize()) == json.loads(expected_json)


def test_error_level_comparison():
    # pylint: disable=too-many-statements, comparison-with-itself
    debug = ErrorLevel.DEBUG
    info = ErrorLevel.INFO
    warn = ErrorLevel.WARN
    error = ErrorLevel.ERROR
    fatal = ErrorLevel.FATAL
    panic = ErrorLevel.PANIC
    disabled = ErrorLevel.DISABLED

    # Test less than
    assert debug < info
    assert info < warn
    assert warn < error
    assert error < fatal
    assert fatal < panic
    assert panic < disabled

    # Test less than or equal
    assert debug <= debug
    assert debug <= info
    assert info <= info
    assert info <= warn
    assert warn <= warn
    assert warn <= error
    assert error <= error
    assert error <= fatal
    assert fatal <= fatal
    assert fatal <= panic
    assert panic <= panic
    assert panic <= disabled
    assert disabled <= disabled

    # Test greater than
    assert info > debug
    assert warn > info
    assert error > warn
    assert fatal > error
    assert panic > fatal
    assert disabled > panic

    # Test greater than or equal
    assert debug >= debug
    assert info >= debug
    assert info >= info
    assert warn >= info
    assert warn >= warn
    assert error >= warn
    assert error >= error
    assert fatal >= error
    assert fatal >= fatal
    assert panic >= fatal
    assert panic >= panic
    assert disabled >= disabled

    # Test equality
    assert debug == debug
    assert info == info
    assert warn == warn
    assert error == error
    assert fatal == fatal
    assert panic == panic
    assert disabled == disabled

    # Test inequality
    assert debug != info
    assert debug != warn
    assert debug != error
    assert debug != fatal
    assert debug != panic
    assert debug != disabled

    assert info != debug
    assert info != warn
    assert info != error
    assert info != fatal
    assert info != panic
    assert info != disabled

    assert warn != debug
    assert warn != info
    assert warn != error
    assert warn != fatal
    assert warn != panic
    assert warn != disabled

    assert error != debug
    assert error != info
    assert error != warn
    assert error != fatal
    assert error != panic
    assert error != disabled

    assert fatal != debug
    assert fatal != info
    assert fatal != warn
    assert fatal != error
    assert fatal != panic
    assert fatal != disabled

    assert panic != debug
    assert panic != info
    assert panic != warn
    assert panic != error
    assert panic != fatal
    assert panic != disabled

    assert disabled != debug
    assert disabled != info
    assert disabled != warn
    assert disabled != error
    assert disabled != fatal
    assert disabled != panic

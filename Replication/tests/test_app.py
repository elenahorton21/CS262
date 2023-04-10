"""
Testing App class functionality.

TODO: Modify after cleaning up data structures.
"""
import pytest
from unittest.mock import patch, mock_open
from testfixtures import compare
import pickle

from app import App, User, Message


@pytest.fixture
def app_data():
    """Returns populated data for App instance."""
    users = {username: User(username) for username in ["John", "Jane", "Bob"]}
    # Add message queue items
    # TODO: Is first argument for Message class the 
    users["Bob"].messages = [Message("John", "Hello"), Message("Jane", "What's up?")]

    return users


def test_save_state(app_data):
    open_mock = mock_open()
    with patch("app.open", open_mock, create=True), \
        patch("app.time.time", return_value=1):
            app = App()
            app.users = app_data
            app.save_state()

    open_mock.assert_called_with("app.pickle", "wb")

    # Check the bytes
    write_file_bytes = open_mock.return_value.write.call_args[0][0]
    deserialized = pickle.loads(write_file_bytes)
    compare(deserialized, app_data)

    # Check the last modified timestamp
    assert app.last_modified_timestamp == 1


def test_init_with_load_data(app_data):
    open_mock = mock_open()
    with patch("app.os.path.isfile", return_value=True), \
        patch("app.pickle.load", return_value=app_data), \
        patch("app.open", open_mock, create=True), \
        patch("app.os.path.getmtime", return_value=1):
            app = App(load_data=True)
    
    open_mock.assert_called_with("app.pickle", "rb")
    assert app.last_modified_timestamp == 1
    compare(app.users, app_data)


def test_init_with_empty_load_data():
    open_mock = mock_open()
    with patch("app.os.path.isfile", return_value=False), \
        patch("app.open", open_mock, create=True), \
        patch("app.time.time", return_value=1):
            app = App(load_data=True)
    
    open_mock.assert_called_with("app.pickle", "wb")
    # Should create an empty file
    write_file_bytes = open_mock.return_value.write.call_args[0][0]
    deserialized = pickle.loads(write_file_bytes)
    compare(deserialized, {})
    # Check the last modified timestamp
    assert app.last_modified_timestamp == 1

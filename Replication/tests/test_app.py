"""
Testing App class functionality.

TODO: Modify after cleaning up data structures.
"""
import pytest
from unittest.mock import patch, mock_open
from testfixtures import compare
import pickle

from src.app import App, User, Message


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
    with patch("src.app.open", open_mock, create=True):
        app = App()
        app.users = app_data
        app.save_state()

    open_mock.assert_called_with("app.pickle", "wb")

    # Check the bytes
    write_file_bytes = open_mock.return_value.write.call_args[0][0]
    deserialized = pickle.loads(write_file_bytes)
    compare(deserialized, app_data)


def test_init_with_load_data(app_data):
    with patch("src.app.pickle.load", return_value=app_data):
        app = App(load_data=True)
    
        compare(app.users, app_data)

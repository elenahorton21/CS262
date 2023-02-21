"""
TODO: Not every test has completely decoupled AppState logic. Seems like 
overkill to do this but we could.
"""

import pytest
from unittest.mock import MagicMock, patch
from testfixtures import compare

from src.server import *
from src.app import AppState


@pytest.fixture
def app_state():
    """Returns an AppState instance with some populated data."""
    users = set(["John", "Jane", "Bob"])
    connections = {"John": 1, "Jane": 2}
    msg_queue = {"Bob": ["Hello", "What's up?"]}

    return AppState(users, connections, msg_queue)


@pytest.fixture
def app_state_data():
    """Returns the above data for an AppState instance. Useful
    when creating a patched version of AppState."""
    users = set(["John", "Jane", "Bob"])
    connections = {"John": 1, "Jane": 2}
    msg_queue = {"Bob": ["Hello", "What's up?"]}

    return {"users": users, "connections": connections, "msg_queue": msg_queue}


def test_register_new_user(app_state):
    # Registering valid new username
    msg = RegisterMessage(username="Jill")
    res = register_service(msg, app_state)
    assert res.success
    assert res.is_new_user


def test_register_previous_user(app_state):
    # Registering valid previous username
    msg = RegisterMessage(username="Bob")
    res = register_service(msg, app_state)
    assert res.success
    assert not res.is_new_user


def test_register_invalid_username(app_state):
    # Registering an invalid username should return error response
    msg = RegisterMessage(username="John_1")
    res = register_service(msg, app_state)
    assert not res.success
    assert res.error == "Username must contain only alphanumeric characters only."


def test_register_active_user(app_state):
    # Registering a username currently used should return error response
    msg = RegisterMessage(username="John")
    res = register_service(msg, app_state)
    assert not res.success
    assert res.error == "Username is already in use."


def test_chat_invalid_user(app_state):
    # Sending a chat to an unregistered username should return error response
    msg = ChatMessage(sender="John", recipient="Jim", text="Hello Jim!")
    res = chat_service(msg, app_state)
    assert not res.success
    assert res.error == "User does not exist."


@patch('src.server.broadcast')
def test_chat_to_all(mock_broadcast, app_state):
    # Sending a message to all active users'
    msg = ChatMessage(sender="John", text="Hello everyone!")
    res = chat_service(msg, app_state)

    # Check that `broadcast` is called correctly 
    exp_call_msg = (BroadcastMessage(sender="John", direct=None, text="Hello everyone!"))
    exp_call_recvs = [1, 2] # We are using integers instead of socket instances here
    actual_call_msg, actual_call_recvs = mock_broadcast.call_args[0]
    compare(exp_call_msg, actual_call_msg)
    compare(exp_call_recvs, actual_call_recvs)

    # Check the response
    assert res.success


@patch('src.server.broadcast')
def test_chat_active_user(mock_broadcast, app_state):
    # Sending a message to an active user
    msg = ChatMessage(sender="John", recipient="Jane", text="Hello Jane!")
    res = chat_service(msg, app_state)

    # Check that `broadcast` is called correctly
    exp_call_msg = (BroadcastMessage(sender="John", direct="Jane", text="Hello Jane!"))
    exp_call_recvs = [1, 2] 
    actual_call_msg, actual_call_recvs = mock_broadcast.call_args[0]
    compare(exp_call_msg, actual_call_msg)
    compare(exp_call_recvs, actual_call_recvs)

    assert res.success

 
@patch('src.server.broadcast')
def test_chat_inactive_user(mock_broadcast, app_state_data):
    # Sending a message to an inactive user
    # NOTE: We don't use the fixture here so that we can mock the queue message
    # function.
    with patch.object(AppState, 'queue_message', return_value=None) as mock_method:
        app_state = AppState(**app_state_data) # Initialize with fixture data
        msg = ChatMessage(sender="John", recipient="Bob", text="Hello Bob!")
        res = chat_service(msg, app_state)

    # Check that `broadcast` is called correctly
    exp_call_msg = (BroadcastMessage(sender="John", direct="Bob", text="Hello Bob!"))
    exp_call_recvs = [1] # Should just be sent back to John
    actual_call_msg, actual_call_recvs = mock_broadcast.call_args[0]
    compare(exp_call_msg, actual_call_msg)
    compare(exp_call_recvs, actual_call_recvs)

    # Check that `app.queue_message` is called correctly
    recipient, queued_msg = mock_method.call_args[0]
    compare(queued_msg, exp_call_msg)
    assert recipient == "Bob"

    # Check response
    assert res.success


def test_list_users(app_state):
    # TODO: Test after implementing wildcard.
    assert False


def test_delete_valid_user(app_state):
    # Delete an inactive user
    msg = DeleteMessage(username="Bob")
    res = delete_service(msg, app_state)

    assert res.success


def test_delete_invalid_user(app_state):
    # Deleting a username that isn't registered should return errror
    msg = DeleteMessage(username="Jill")
    res = delete_service(msg, app_state)

    assert not res.success
    assert res.error == "Username 'Jill' is not registered."


def test_delete_active_user(app_state):
    # Deleting an active user should return error
    msg = DeleteMessage(username="Jane")
    res = delete_service(msg, app_state)

    assert not res.success
    assert res.error == "Cannot delete an active user."


def test_msg_queue():
    # TODO: Check edge cases with buffer size
    assert False


def test_handle_register_user(app_state_data):
    # Successfully registering a username should add connection to app state
    with patch.object(AppState, 'add_connection', return_value=None) as mock_method:
        app_state = AppState(**app_state_data)
        socket = MagicMock()
        socket.getsockname.return_value = "Jill's socket" # Give the mock this function
        msg = RegisterMessage(username="Jill")
        res = handle_message(msg, app_state, socket) # Use int values instead of socket

    mock_method.assert_called_with("Jill", socket)    
    assert res.success


def test_disconnect_client(app_state_data):
    with patch.object(AppState, 'remove_connection', return_value=None) as mock_method:
        app_state = AppState(**app_state_data)
        socket = MagicMock()
        socket.getsockname.return_value = "Socket"
        disconnect_client(socket, app_state)

    mock_method.assert_called_with(socket)

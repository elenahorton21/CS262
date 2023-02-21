"""
Testing AppState functionality.

NOTE: Using integers in place of Socket objects for connections.
NOTE: Using strings instead of BroadcastMessage objects for message queue values.
"""

import pytest

from src.app import AppState, InvalidUserError


@pytest.fixture
def app_state():
    """Returns an AppState instance with some populated data."""
    users = set(["John", "Jane", "Bob"])
    connections = {"John": 1, "Jane": 2}
    msg_queue = {"Bob": ["Hello", "What's up?"]}

    return AppState(users, connections, msg_queue)


@pytest.fixture
def empty_app_state():
    """Returns an empty AppState instance."""
    return AppState()


def list_members_equal(list1, list2):
    """Returns True if the lists have the same items, regardless of order."""
    return not set(list1) ^ set(list2)


def test__get_connection_username(app_state):
    assert app_state._get_connection_username(1) == "John"


def test_is_valid_user(app_state):
    assert app_state.is_valid_user("John")
    assert app_state.is_valid_user("Bob")
    assert not app_state.is_valid_user("Joe")


def test_get_all_connections(app_state):
    assert list_members_equal(app_state.get_all_connections(), [1, 2])


def test_get_user_connection(app_state):
    assert app_state.get_user_connection("Jane") == 2
    assert app_state.get_user_connection("Bob") == None


def test_list_users(app_state):
    assert list_members_equal(app_state.list_users(), ["John", "Jane", "Bob"])


def test_register_invalid_username(app_state):
    # Check that the correct exceptions are raised
    with pytest.raises(InvalidUserError) as excinfo1:
        app_state.register_user("John")
    with pytest.raises(ValueError) as excinfo2:
        app_state.register_user("...")
    assert str(excinfo1.value) == "Username is already in use."
    assert str(excinfo2.value) == "Username must contain only alphanumeric characters only."


def test_register_new_username(app_state):
    # Check that registering a valid username is successful
    is_new_user = app_state.register_user("Dan")
    assert is_new_user
    assert app_state._users == set(["John", "Jane", "Bob", "Dan"])
    

def test_register_previous_username(app_state):
    # Check registering an inactive username
    is_new_user = app_state.register_user("Bob")
    assert not is_new_user
    assert app_state._users == set(["John", "Jane", "Bob"])


def test_delete_invalid_user(app_state):
    # Check that the correct exception is raised with unregistered username
    with pytest.raises(InvalidUserError) as excinfo1:
        app_state.delete_user("Dan")
    assert str(excinfo1.value) == "Username 'Dan' is not registered."


def test_delete_active_user(app_state):
    # Check that the correct exception is raised with active user
    with pytest.raises(ValueError) as excinfo2:
        app_state.delete_user("Jane")
    assert str(excinfo2.value) == "Cannot delete an active user."


def test_delete_success(app_state):
    # Check that deleting a valid username is successful
    app_state.delete_user("Bob")
    app_state._msg_queue.get("Bob", None) == None
    app_state._users == set(["John", "Jane"])


def test_delete_with_msg_queue(app_state):
    # Check that deleting a valid username without queued messages is successful
    app_state._connections.pop("Jane") # Remove Jane from active connections
    app_state.delete_user("Jane")
    app_state._msg_queue.get("Jane", None) == None
    app_state._users == set(["John"])


def test_add_connection_user_duplicate(app_state):
    # Test adding a username currently being used
    with pytest.raises(InvalidUserError) as excinfo:
        app_state.add_connection("John", 3)
    assert str(excinfo.value) == "Username is already connected to a socket."


def test_add_connection_socket_duplicate(app_state):
    # Test adding a socket currently being used
    with pytest.raises(ValueError) as excinfo:
        app_state.add_connection("Dan", 2)
    assert str(excinfo.value) == "Socket is already associated with another user."


def test_add_connection_success(app_state):
    # Test success case
    app_state.add_connection("Dan", 3)
    assert app_state._connections["Dan"] == 3


def test_remove_connection(app_state):
    app_state.remove_connection(2)
    app_state._connections == {"John": 1}


def test_queue_message_invalid(app_state):
    # Test exception for invalid username
    with pytest.raises(InvalidUserError) as excinfo:
        app_state.queue_message("Dan", "Hello")


def test_queue_message_new(app_state):
    # Test adding first message for user to queue
    app_state.queue_message("John", "Hello")
    assert app_state._msg_queue['John'] == ["Hello"]


def test_queue_message_existing(app_state):
    # Test adding a message to existing queue
    app_state.queue_message("Bob", "Hi")
    assert app_state._msg_queue["Bob"] == ["Hello", "What's up?", "Hi"]


def test_get_queued_messages(app_state):
    res = app_state.get_queued_messages("Bob")

    assert res == ["Hello", "What's up?"]
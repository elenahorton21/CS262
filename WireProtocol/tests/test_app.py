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
    msg_queue = {"Jane": ["Hello", "What's up?"]}

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

def test_register_user(app_state):
    # Check that the correct exceptions are raised
    with pytest.raises(ValueError) as excinfo1:
        app_state.register_user("John")
    with pytest.raises(ValueError) as excinfo2:
        app_state.register_user("...")
    assert str(excinfo1.value) == "Username is already registered."
    assert str(excinfo2.value) == "Username must contain only alphanumeric characters only."

    # Check that registering a valid username is successful
    app_state.register_user("Dan")
    assert app_state._users == set(["John", "Jane", "Bob", "Dan"])

def test_delete_user(app_state):
    # Check that the correct exception is raised
    with pytest.raises(InvalidUserError) as excinfo:
        app_state.delete_user("Dan")

    # Check that deleting a valid username is successful
    app_state.delete_user("Jane")
    app_state._msg_queue.get("Jane", None) == None
    app_state._users == set(["John", "Bob"])

def test_add_connection(app_state):
    # Test adding a username currently being used
    with pytest.raises(ValueError) as excinfo:
        app_state.add_connection("John", 3)
    assert str(excinfo.value) == "Username is currently being used."

    # Test existing user login, should return True.
    is_existing = app_state.add_connection("Bob", 3)
    assert is_existing 
    assert app_state._connections == {"John": 1, "Jane": 2, "Bob": 3}

    # Test registering a new username
    is_existing = app_state.add_connection("Dan", 4)
    assert not is_existing
    assert app_state._connections == {"John": 1, "Jane": 2, "Bob": 3, "Dan": 4}

def test_remove_connection(app_state):
    app_state.remove_connection(2)
    app_state._connections == {"John": 1}

def test_queue_message(app_state):
    # Test exception for invalid username
    with pytest.raises(InvalidUserError) as excinfo:
        app_state.queue_message("Dan", "Hello")

    # Test adding first message for user to queue
    app_state.queue_message("John", "Hello")
    assert app_state._msg_queue['John'] == ["Hello"]

    # Test adding a message to existing queue
    app_state.queue_message("Jane", "Hi")
    assert app_state._msg_queue["Jane"] == ["Hello", "What's up?", "Hi"]
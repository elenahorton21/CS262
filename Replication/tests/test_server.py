import pytest
from unittest.mock import patch, PropertyMock, MagicMock
import pickle
from testfixtures import compare
import multiprocessing


from server import ChatServer, Replica
from app import App, Message, User
import proto.chat_pb2 as chat


@pytest.fixture
def mock_primary():
    """Return a primary ChatServer where dependecies are mocked."""
    with patch("server.App", return_value=App()):
        server = ChatServer(is_primary=True)
        return server


@pytest.fixture
def mock_backup():
    """Return a backup ChatServer where dependencies are mocked."""
    with patch("server.App", return_value=App()):
        server = ChatServer()
        return server
    

@pytest.fixture
def app_data():
    """Returns populated data for App instance."""
    users = {username: User(username) for username in ["John", "Jane", "Bob"]}
    # Add message queue items
    # TODO: Is first argument for Message class the 
    users["Bob"].messages = [Message("John", "Hello"), Message("Jane", "What's up?")]

    return users


def test__listen_for_state_updates(mock_backup, app_data):
    # Mock the return value of StateUpdateStream
    with patch.object(mock_backup, 'conns') as mock_conns, \
        patch.object(mock_backup, '_handle_state_update') as mock_method:
            mock_conns.__getitem__().StateUpdateStream.return_value = [chat.StateUpdate(state=pickle.dumps(app_data))]
            mock_backup._listen_for_state_updates(0)

    # Check that backup's data is now correct
    compare(mock_backup.app.users, app_data)
    # Check that `_handle_state_update` is called
    mock_method.assert_called_once()


def test__listen_for_state_updates_fails(mock_backup):
    # Mock the return value of StateUpdateStream
    mock_conn = MagicMock()
    mock_backup.conns = {0: mock_conn}
    mock_conn.StateUpdateStream.side_effect = Exception("Mocked socket close")
    mock_backup._listen_for_state_updates(0)

    # The backup should be primary now
    assert mock_backup.is_primary 
    assert mock_backup.conns == {}


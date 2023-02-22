import pytest
from testfixtures import compare

from src.protocol import *

# TODO: Test edge cases where text exceeds buffer limits.

@pytest.fixture
def queued_msgs():
    """A list of BroadcastMessage instances."""
    msg1 = BroadcastMessage(sender="John", text="Hello")
    msg2 = BroadcastMessage(sender="John", text="What's up?")
    msg3 = BroadcastMessage(sender="Joe", text="How's it going?")

    return [msg1, msg2, msg3]


@pytest.fixture
def max_length_broadcast():
    """A BroadcastMessage with max length text."""
    return BroadcastMessage(sender="John", text="A"*280)


def test_encode_register_msg():
    msg = RegisterMessage(username="John")
    expected = "REG<SEP>John<EOM>"
    assert msg.encode_() == expected.encode()


def test_decode_register_msg():
    serialized = "REG<SEP>John" # EOM token is assumed to be removed
    res = deserialize_client_message(serialized)
    expected = RegisterMessage(username="John")
    compare(res, expected)


def test_encode_chat_msg_all():
    msg = ChatMessage(sender="John", recipient=None, text="Hello all!")
    expected = "MSG<SEP>John<SEP>^<SEP>Hello all!<EOM>"
    assert msg.encode_() == expected.encode()


def test_encode_chat_msg_big():
    # If the chat message is too big, should raise error
    with pytest.raises(ValueError) as excinfo:
        _ = ChatMessage(sender="John", recipient="Bob", text="A"*281)
    assert str(excinfo.value) == "Messages have a limit of 280 characters."


def test_decode_chat_msg_all():
    serialized =  "MSG<SEP>John<SEP>^<SEP>Hello all!"
    res = deserialize_client_message(serialized)
    expected = ChatMessage(sender="John", recipient=None, text="Hello all!")
    compare(res, expected)


def test_encode_chat_dm():
    max_length_msg = "A" * 280
    msg = ChatMessage(sender="John", recipient="Bob", text=max_length_msg)
    expected = f"MSG<SEP>John<SEP>Bob<SEP>{max_length_msg}<EOM>"
    assert msg.encode_() == expected.encode()


def test_decode_chat_dm():
    serialized =  "MSG<SEP>John<SEP>Bob<SEP>Hello Bob!"
    res = deserialize_client_message(serialized)
    expected = ChatMessage(sender="John", recipient="Bob", text="Hello Bob!")
    compare(res, expected)


def test_encode_list_msg():
    msg = ListMessage(wildcard=".*J")
    expected = "LST<SEP>.*J<EOM>"
    assert msg.encode_() == expected.encode()


def test_decode_list_msg():
    serialized = "LST<SEP>.*J"
    res = deserialize_client_message(serialized)
    expected = ListMessage(wildcard=".*J")
    compare(res, expected)


def test_encode_delete_msg():
    msg = DeleteMessage(username="John")
    expected = "DEL<SEP>John<EOM>"
    assert msg.encode_() == expected.encode()


def test_decode_delete_msg():
    serialized = "DEL<SEP>John"
    res = deserialize_client_message(serialized)
    expected = DeleteMessage(username="John")
    compare(res, expected)


def test_encode_queue_msg():
    msg = QueueMessage(username="John")
    expected = "QUE<SEP>John<EOM>"
    assert msg.encode_() == expected.encode()


def test_decode_queue_msg():
    serialized = "QUE<SEP>John"
    res = deserialize_client_message(serialized)
    expected = QueueMessage(username="John")
    compare(res, expected)


def test_decode_unknown_client_msg():
    with pytest.raises(ValueError) as excinfo:
        _ = deserialize_client_message("Bad message format")
    assert str(excinfo.value) == "Unknown message type header received from client."


def test_encode_register_response():
    res = RegisterResponse(success=True, is_new_user=False)
    expected = "RESR<SEP>1<SEP><SEP>0<EOM>"
    assert res.encode_() == expected.encode()


def test_decode_register_response():
    serialized = "RESR<SEP>0<SEP>There was an error!<SEP>"
    res = deserialize_server_message(serialized)
    expected = RegisterResponse(success=False, error="There was an error!")
    compare(res, expected)


def test_encode_list_response():
    users = ["A"*12 for _ in range(30)] # Test max length
    res = ListResponse(success=True, users=users)
    expected = "RESL<SEP>1<SEP><SEP>0<SEP>" + "<SEP>".join(users) + "<EOM>"
    assert res.encode_() == expected.encode()


def test_decode_list_response_empty():
    serialized = "RESL<SEP>1<SEP><SEP>0"
    res = deserialize_server_message(serialized)
    expected = ListResponse(success=True, users=[])
    compare(res, expected)


def test_decode_server_buffer(queued_msgs):
    # Concatenate with an empty byte string
    buffer = b"".join([msg.encode_() for msg in queued_msgs])

    msgs = decode_server_buffer(buffer)

    # `compare` lets us easily check that the parameters are equal
    # even though the instances are different
    compare(msgs[0], queued_msgs[0])
    compare(msgs[1], queued_msgs[1])
    compare(msgs[2], queued_msgs[2])


def test_encode_msg_queue(max_length_broadcast):
    queued_msgs = [max_length_broadcast for _ in range(20)] # 10 max length messages
    res = encode_msg_queue(queued_msgs)
    
    # This should return 7 items
    assert len(res) == 7
    # Check that each item is less than MAX_BUFFER_SIZE
    assert all([len(buffer) <= MAX_BUFFER_SIZE for buffer in res])


def test_decode_msg_queue(max_length_broadcast):
    queued_msgs = [max_length_broadcast for _ in range(20)] # 10 max length messages
    res = encode_msg_queue(queued_msgs)

    msgs = []
    for buffer in res:
        msgs += decode_server_buffer(buffer)

    assert len(msgs) == 20
    for msg in msgs:
        compare(max_length_broadcast, msg)
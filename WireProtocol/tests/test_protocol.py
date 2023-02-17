import pytest
from testfixtures import compare

from src.protocol import *


def test_decode_server_buffer():
    # Create a buffer with multiple messages
    msg1 = BroadcastMessage(sender="John", text="Hello")
    msg2 = BroadcastMessage(sender="Jane", text="What's up?")
    msg3 = BroadcastMessage(sender="Joe", text="How's it going?")
    # Concatenate with an empty byte string
    buffer = b"".join([msg1.encode_(), msg2.encode_(), msg3.encode_()])

    msgs = decode_server_buffer(buffer)

    # `compare` lets us easily check that the parameters are equal
    # even though the instances are different
    compare(msgs[0], msg1)
    compare(msgs[1], msg2)
    compare(msgs[2], msg3)



# def test_from_str_register():
#   text = "USERNAME|John"
#   msg = Message.from_str(text)
#   assert msg.msg_type == MessageType.REGISTER
#   assert msg.data == {"username": "John"}


# def test_from_str_message():
#   text = "MESSAGE|John|Alice|Hello what's up?"
#   msg = Message.from_str(text)
#   assert msg.msg_type == MessageType.MESSAGE
#   assert msg.data == {"from": "John", "to": "Alice", "msg": "Hello what's up?"}


# def test_from_str_list():
#   text = "LIST|wild"
#   msg = Message.from_str(text)
#   assert msg.msg_type == MessageType.LIST
#   assert msg.data == {"wildcard": "wild"}


# def test_from_str_delete():
#   text = "DELETE|John"
#   msg = Message.from_str(text)
#   assert msg.msg_type == MessageType.DELETE
#   assert msg.data == {"username": "John"}


# def test_to_str_register():
#   msg = Message(MessageType.REGISTER, {"username": "John"})
#   assert msg.to_str() == "USERNAME|John"
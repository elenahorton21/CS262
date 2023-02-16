# import pytest

# from src.protocol import *


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
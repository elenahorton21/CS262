# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chat.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nchat.proto\x12\x04\x63hat\"\x1f\n\x0bUserRequest\x12\x10\n\x08username\x18\x01 \x01(\t\"@\n\x0eMessageRequest\x12\x0c\n\x04user\x18\x01 \x01(\t\x12\x0f\n\x07to_user\x18\x02 \x01(\t\x12\x0f\n\x07message\x18\x03 \x01(\t\"\x1a\n\nGetRequest\x12\x0c\n\x04user\x18\x01 \x01(\t\"\x1f\n\x0bListRequest\x12\x10\n\x08wildcard\x18\x01 \x01(\t\"\x1c\n\tChatReply\x12\x0f\n\x07message\x18\x01 \x01(\t2\x91\x02\n\x04\x43hat\x12\x33\n\x0b\x63reate_user\x12\x11.chat.UserRequest\x1a\x0f.chat.ChatReply\"\x00\x12\x32\n\nlist_users\x12\x11.chat.ListRequest\x1a\x0f.chat.ChatReply\"\x00\x12\x33\n\x0b\x64\x65lete_user\x12\x11.chat.UserRequest\x1a\x0f.chat.ChatReply\"\x00\x12\x37\n\x0csend_message\x12\x14.chat.MessageRequest\x1a\x0f.chat.ChatReply\"\x00\x12\x32\n\x0bget_message\x12\x10.chat.GetRequest\x1a\x0f.chat.ChatReply\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'chat_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _USERREQUEST._serialized_start=20
  _USERREQUEST._serialized_end=51
  _MESSAGEREQUEST._serialized_start=53
  _MESSAGEREQUEST._serialized_end=117
  _GETREQUEST._serialized_start=119
  _GETREQUEST._serialized_end=145
  _LISTREQUEST._serialized_start=147
  _LISTREQUEST._serialized_end=178
  _CHATREPLY._serialized_start=180
  _CHATREPLY._serialized_end=208
  _CHAT._serialized_start=211
  _CHAT._serialized_end=484
# @@protoc_insertion_point(module_scope)

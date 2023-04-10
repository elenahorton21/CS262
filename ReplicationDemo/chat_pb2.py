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


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nchat.proto\x12\x04\x63hat\"\x1f\n\x0bUserRequest\x12\x10\n\x08username\x18\x01 \x01(\t\"E\n\x0eMessageRequest\x12\x11\n\tfrom_user\x18\x01 \x01(\t\x12\x0f\n\x07to_user\x18\x02 \x01(\t\x12\x0f\n\x07message\x18\x03 \x01(\t\"3\n\rDeleteRequest\x12\x11\n\tfrom_user\x18\x01 \x01(\t\x12\x0f\n\x07to_user\x18\x02 \x01(\t\"\x1a\n\nGetRequest\x12\x0c\n\x04user\x18\x01 \x01(\t\"\x1f\n\x0bListRequest\x12\x10\n\x08wildcard\x18\x01 \x01(\t\"\x1c\n\tChatReply\x12\x0f\n\x07message\x18\x01 \x01(\t\" \n\rServerRequest\x12\x0f\n\x07message\x18\x01 \x01(\t\"\x07\n\x05\x45mpty\"\x1e\n\tHeartbeat\x12\x11\n\ttimestamp\x18\x01 \x01(\t\"\x1c\n\x0bStateUpdate\x12\r\n\x05state\x18\x01 \x01(\x0c\x32\xea\x03\n\x04\x43hat\x12\x33\n\x0b\x63reate_user\x12\x11.chat.UserRequest\x1a\x0f.chat.ChatReply\"\x00\x12\x32\n\nlist_users\x12\x11.chat.ListRequest\x1a\x0f.chat.ChatReply\"\x00\x12\x35\n\x0b\x64\x65lete_user\x12\x13.chat.DeleteRequest\x1a\x0f.chat.ChatReply\"\x00\x12\x37\n\x0csend_message\x12\x14.chat.MessageRequest\x1a\x0f.chat.ChatReply\"\x00\x12\x32\n\x0bget_message\x12\x10.chat.GetRequest\x1a\x0f.chat.ChatReply\"\x00\x12\x36\n\x0b\x63hat_stream\x12\x14.chat.MessageRequest\x1a\x0f.chat.ChatReply0\x01\x12\x33\n\x0blogout_user\x12\x11.chat.UserRequest\x1a\x0f.chat.ChatReply\"\x00\x12\x35\n\x11StateUpdateStream\x12\x0b.chat.Empty\x1a\x11.chat.StateUpdate0\x01\x12\x31\n\x0fHeartbeatStream\x12\x0b.chat.Empty\x1a\x0f.chat.Heartbeat0\x01\x62\x06proto3')


_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'chat_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _USERREQUEST._serialized_start=20
  _USERREQUEST._serialized_end=51
  _MESSAGEREQUEST._serialized_start=53
  _MESSAGEREQUEST._serialized_end=122
  _DELETEREQUEST._serialized_start=124
  _DELETEREQUEST._serialized_end=175
  _GETREQUEST._serialized_start=177
  _GETREQUEST._serialized_end=203
  _LISTREQUEST._serialized_start=205
  _LISTREQUEST._serialized_end=236
  _CHATREPLY._serialized_start=238
  _CHATREPLY._serialized_end=266
  _SERVERREQUEST._serialized_start=268
  _SERVERREQUEST._serialized_end=300
  _EMPTY._serialized_start=302
  _EMPTY._serialized_end=309
  _HEARTBEAT._serialized_start=311
  _HEARTBEAT._serialized_end=341
  _STATEUPDATE._serialized_start=343
  _STATEUPDATE._serialized_end=371
  _CHAT._serialized_start=374
  _CHAT._serialized_end=864
# @@protoc_insertion_point(module_scope)

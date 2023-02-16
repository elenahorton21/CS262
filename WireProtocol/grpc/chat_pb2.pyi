from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ChatReply(_message.Message):
    __slots__ = ["message"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class GetRequest(_message.Message):
    __slots__ = ["user"]
    USER_FIELD_NUMBER: _ClassVar[int]
    user: str
    def __init__(self, user: _Optional[str] = ...) -> None: ...

class ListRequest(_message.Message):
    __slots__ = ["wildcard"]
    WILDCARD_FIELD_NUMBER: _ClassVar[int]
    wildcard: str
    def __init__(self, wildcard: _Optional[str] = ...) -> None: ...

class MessageRequest(_message.Message):
    __slots__ = ["message", "user", "username"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    message: str
    user: str
    username: str
    def __init__(self, user: _Optional[str] = ..., username: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class UserRequest(_message.Message):
    __slots__ = ["username"]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    username: str
    def __init__(self, username: _Optional[str] = ...) -> None: ...

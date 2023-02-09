"""Defines message schema."""


from enum import Enum


class MessageType(Enum):
  REGISTER = "USERNAME"
  MESSAGE = "MESSAGE"
  LIST = "LIST"
  DELETE = "DELETE"


class Message:
  def __init__(self, msg_type, data):
    self.msg_type = msg_type
    self.data = data # Dictionary format

  def to_str(self):
    """
    TODO: We can modify this to reduce the payload size, make fixed size, etc.
    """
    # Right now only MESSAGE types have multiple fields.
    # We need to concat the values in the right order.
    if self.msg_type == MessageType.MESSAGE:
      return f"{self.msg_type}|{self.data['from']}|{self.data['to']}|{self.data['msg']}"
    else:
      return "|".join([self.msg_type.value] + list(self.data.values()))
    
  @classmethod
  def from_str(cls, raw_msg):
    """
    Convert string into Message object. We can also use this as a factory
    method if we want subclasses for message types.
    TODO: Should have handling of improper formats.
    """
    content = raw_msg.split("|")
    if content[0] == MessageType.REGISTER.value:
      msg_type = MessageType.REGISTER
      data = {"username": content[1]}
    elif content[0] == MessageType.MESSAGE.value:
      msg_type = MessageType.MESSAGE
      data = {"from": content[1], "to": content[2], "msg": content[3]}
    elif content[0] == MessageType.LIST.value:
      msg_type = MessageType.LIST
      data = {"wildcard": content[1]}
    elif content[0] == MessageType.DELETE.value:
      msg_type = MessageType.DELETE
      data = {"username": content[1]}
    else:
      raise ValueError("Unknown message type header.")
      
    return Message(msg_type, data)



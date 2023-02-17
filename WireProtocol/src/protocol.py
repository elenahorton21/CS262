"""
Defines message schema.
NOTE: We can modify these classes to encode header-body messages to handle potential buffer issues.
TODO: Add check that encoded message is smaller than `MAX_BUFFER_SIZE`.
TODO: Add end of message token, otherwise buffer can read multiple messages at once.
TODO: Probably want to have the conversion to bytes handled better.
TODO: Refactor shared components.
TODO: We should use smaller `enc_header` values, e.g. integers.
TODO: Unsure about design of Response messages.
"""

class Message:
    """
    Base class for protocol messages.
    TODO: Can have methods for checking encoding byte size, etc.
    """
    separator_token = "<SEP>"

    def encode_(): # Using this to distinguish from generic encode() method
        raise NotImplementedError


####################
### Client Messages
####################

class RegisterMessage(Message):
    enc_header = "REGISTER"
    
    def __init__(self, username):
        self.username = username

    def encode_(self):
        out_str = self.separator_token.join([self.enc_header, self.username])
        return out_str.encode()


class ChatMessage(Message):
    """
    Message from client to server requesting message sent.
    """
    enc_header = "MESSAGE"

    def __init__(self, sender, text, recipient=None):
        self.sender = sender
        self.text = text
        self.recipient = recipient

    def encode_(self):
        # We can encode "TO_ALL" as ^ if we enforce that usernames
        # must contain alphanumeric characters.
        enc_recipient = self.recipient if self.recipient else "^"
        out_str = self.separator_token.join([self.enc_header, self.sender, enc_recipient, self.text])
        return out_str.encode()

    def to_broadcast(self):
        """
        Return the corresponding BroadcastMessage.
        Putting this here in case we have some formatting stuff, e.g. removing
        certain characters.
        """
        direct = (self.recipient != None)
        return BroadcastMessage(sender=self.sender, direct=direct, text=self.text)

        
class ListMessage(Message):
    enc_header = "LIST"

    def __init__(self, wildcard=None):
        self.wildcard = wildcard

    def encode_(self):
        str_items = [self.enc_header, self.wildcard] if self.wildcard else [self.enc_header]
        out_str = self.separator_token.join(str_items)
        return out_str.encode()


class DeleteMessage(Message):
    enc_header = "DELETE"

    def __init__(self, username):
        self.username = username

    def encode_(self):
        out_str = self.separator_token.join([self.enc_header, self.username])
        return out_str.encode()


####################
### Server Messages
####################

class Response(Message):
    """
    Base class for server responses to messages. Each Response object has
    a `success` and `error` field.
    """
    enc_header = "RES"

    def __init__(self, success, error=None):
        self.success = success # Boolean
        self.error = error if error else ""

    def encode_(self):
        out_str = self.separator_token.join([self.enc_header, str(int(self.success)), self.error])
        return out_str.encode()


class RegisterResponse(Response):
    """Response format for registering username."""
    enc_header = "RES-R"


class ChatResponse(Response):
    """Response format for chat messages."""
    enc_header = "RES-C"


class ListResponse(Response):
    """Response format for listing users."""
    enc_header = "RES-L"

    def __init__(self, success, error=None, users=[]):
        """
        Args:
            users ([str]): List of usernames.
        """
        super().__init__(success, error)
        self.users = users
    
    def encode_(self):
        str_items = [self.enc_header, str(int(self.success)), self.error] + self.users
        out_str = self.separator_token.join(str_items)
        return out_str.encode()
    

class DeleteResponse(Response):
    enc_header = "RES-D"


class BroadcastMessage(Message):
    """Class for server's execution of ChatMessage requests.
    TODO: Can add metadata like when the message was sent.
    """
    enc_header = "BROAD"

    def __init__(self, sender, text, direct):
        self.sender = sender
        self.text = text
        self.direct = direct

    def encode_(self):
        direct_enc = str(int(self.direct))
        out_str = self.separator_token.join([self.enc_header, self.sender, direct_enc, self.text])
        return out_str.encode()


####################
### Decoding
####################

def decode_client_message(msg):
    """Factory method for converting read buffer data to appropriate Message subclass."""
    msg = msg.decode() # Need to convert back to string
    content = msg.split(Message.separator_token)

    if content[0] == RegisterMessage.enc_header:
        return RegisterMessage(username=content[1])
    elif content[0] == ChatMessage.enc_header:
        recipient = None if content[2] == "^" else content[2]
        return ChatMessage(sender=content[1], recipient=recipient, text=content[3])
    elif content[0] == ListMessage.enc_header:
        wildcard = content[1] if len(content) > 1 else None
        return ListMessage(wildcard=wildcard)
    elif content[0] == DeleteMessage.enc_header:
        return DeleteMessage(username=content[1])
    else:
      raise ValueError("Unknown message type header received from client.")


def decode_server_message(msg):
    """Factory method for converting read buffer data on client side to appropriate Message subclass."""
    msg = msg.decode() # Need to convert back to string
    content = msg.split(Message.separator_token)
    print(content)
    if content[0] == RegisterResponse.enc_header:
        return RegisterResponse(success=bool(int(content[1])), error=content[2])
    elif content[0] == ChatResponse.enc_header:
        return ChatResponse(success=bool(int(content[1])), error=content[2])
    elif content[0] == DeleteResponse.enc_header:
        return DeleteResponse(success=bool(int(content[1])), error=content[2])
    elif content[0] == ListResponse.enc_header:
        users = content[3:] if len(content) > 2 else None
        return ListResponse(success=bool(int(content[1])), error=content[2], users=users)
    elif content[0] == BroadcastMessage.enc_header:
        return BroadcastMessage(sender=content[1], direct=bool(int(content[2])), text=content[3])
    else:
        raise ValueError("Unknown message type header received from server.")
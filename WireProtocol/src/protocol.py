"""
Defines message schema. Each message has the format "[enc_header][sep_token]data...[sep_token][EOM]",
where data is a sequence of strings joined by `sep_token` of variable length 
dependent on the message type.

NOTE: We can modify these classes to encode header-body messages to handle potential buffer issues.
TODO: pytest is throwing errors when I import config.
"""
# from config import config


# MAX_BUFFER_SIZE = config["MAX_BUFFER_SIZE"]
MAX_BUFFER_SIZE = 1024


class Message:
    """
    Base class for protocol messages. Handles the shared functionality
    for converting a Message object to an encoded string, and checking that
    the byte length is smaller than MAX_BUFFER_SIZE.
    """
    separator_token = "<SEP>"
    EOM_token = "<EOM>" # End of message token
    enc_header = None

    def _data_items(self):
        """
        Return the message data as a list of strings. Implemented in
        each child class.
        
        Args:
            None

        Returns:
            List[str]: The items to concatenate in encoded string.    
        """
        raise NotImplementedError
    
    def encode_(self):
        """Returns the encoded string for the message."""
        # Message items are the encoding header, any message data items, and EOM
        msg_items = [self.enc_header] + self._data_items()
        out_str = self.separator_token.join(msg_items) + self.EOM_token
        out_str = out_str.encode()
        # Check that the byte length is less than MAX_BUFFER_SIZE
        if len(out_str) < MAX_BUFFER_SIZE:
            return out_str
        else:
            raise ValueError("Message byte length exceeds limit.")


####################
### Client Messages
####################

class RegisterMessage(Message):
    enc_header = "REG"
    
    def __init__(self, username):
        self.username = username

    def _data_items(self):
        return [self.username]


class ChatMessage(Message):
    """
    Message from client to server requesting message sent.
    """
    enc_header = "MSG"
    text_char_lim = 280 # Maximum number of characters for each message


    def __init__(self, sender, text, recipient=None):
        # Check that `text` is less than character limit
        if len(text) > self.text_char_lim:
            raise ValueError("Messages have a limit of 280 characters.")
        
        self.sender = sender
        self.text = text
        self.recipient = recipient

    def _data_items(self):
        # Use "^" as the string representation of sending to all active users
        recipient_str = self.recipient if self.recipient else "^"
        return [self.sender, recipient_str, self.text]
    
    def to_broadcast(self):
        """
        Return the corresponding BroadcastMessage.
        TODO: Putting this here in case we have some formatting stuff, e.g. removing
        certain characters.
        """
        direct = (self.recipient != None)
        return BroadcastMessage(sender=self.sender, direct=direct, text=self.text)

        
class ListMessage(Message):
    enc_header = "LST"

    def __init__(self, wildcard=None):
        self.wildcard = wildcard

    def _data_items(self):
        """TODO: Fix when finished handling wildcard."""
        return [self.wildcard] if self.wildcard else ["*"]


class DeleteMessage(Message):
    enc_header = "DEL"

    def __init__(self, username):
        self.username = username

    def _data_items(self):
        return [self.username]


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
        """
        Initialize Response instance.

        Args:
            success (bool): True if the message was handled successfully.
            error (str, Optional): Error message.

        Returns:
            Response
        """
        self.success = success # Boolean
        self.error = error if error else ""

    def _data_items(self):
        success_str = str(int(self.success)) # Convert bool to 1/0 string
        return [success_str, self.error]


class RegisterResponse(Response):
    """Response format for registering username."""
    enc_header = "RESR"


class ChatResponse(Response):
    """Response format for chat messages."""
    enc_header = "RESC"


class ListResponse(Response):
    """Response format for listing users."""
    enc_header = "RESL"

    def __init__(self, success, error=None, users=[]):
        """
        Initialize ListResponse instance.

        Args:
            success (bool): True if the message was handled successfully.
            error (str, Optional): Error message.
            users ([str]): List of usernames.

        Returns:
            ListResponse
        """
        super().__init__(success, error)
        self.users = users
    
    def _data_items(self):
        # In addition to success and error fields, we add users as a list of strings
        return super()._data_items() + self.users
    

class DeleteResponse(Response):
    """Response format for delete messages."""
    enc_header = "RESD"


class BroadcastMessage(Message):
    """Class for server's execution of ChatMessage requests.
    TODO: Can add metadata like when the message was sent.
    """
    enc_header = "BRO"

    def __init__(self, sender, text, direct=False):
        self.sender = sender
        self.text = text
        self.direct = direct

    def _data_items(self):
        # Cast self.direct to string representation
        direct_str = str(int(self.direct)) 
        return [self.sender, direct_str, self.text]
    

####################
### Decoding
####################
"""
TODO: Unsure if we need to handle decoding multiple messages from the client,
since multiple messages are never sent in one function call.
"""

def decode_buffer(buffer):
    """
    Decode an encoded string into a list of messages. For each message, we call
    `decode_server_message` to convert it into a Message instance.

    TODO: This does not handle the case where the encoded string contains
    an incomplete message at the end, which could happen if the buffer holds more
    data than MAX_BUFFER_SIZE.
    """
    decoded_str = buffer.decode()
    msgs = decoded_str.split(Message.EOM_token)

    # If we have received a sequence of valid messages, the last token
    # should be EOM_token, so the last item returned by `split()` should
    # be "". Otherwise, raise an exception.
    if msgs[-1] != "":
        raise ValueError("Buffer contains incomplete message.")
    
    # Remove the empty string from list
    msgs = msgs[:-1]

    # Decode each message and return list
    return msgs


def decode_server_buffer(buffer):
    msgs = decode_buffer(buffer)

    return [_decode_server_message(msg) for msg in msgs]


def decode_client_buffer(buffer):
    msgs = decode_buffer(buffer)

    return [_decode_client_message(msg) for msg in msgs]


def _decode_client_message(msg):
    """Factory method for converting an encoded message to appropriate Message subclass."""
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


def _decode_server_message(msg):
    """
    Factory method for converting decoded string on client side to appropriate Message subclass.
    
    Args:
        msg (str): The decoded message string.

    Returns:
        Message: Returns the appropriate subclass based on the string header.
    """
    content = msg.split(Message.separator_token)

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
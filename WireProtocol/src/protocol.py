"""
Defines message schema. Each message has the format "[enc_header][sep_token]data...[sep_token][EOM]",
where data is a sequence of strings joined by `sep_token` of variable length 
dependent on the message type.

NOTE: We can modify these classes to encode header-body messages to handle potential buffer issues.
TODO: pytest is throwing errors when I import config.
"""
import logging

from src.config import config


# Logging
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)


MAX_BUFFER_SIZE = config["MAX_BUFFER_SIZE"]


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
    Client message for sending a chat.
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
        return BroadcastMessage(sender=self.sender, direct=self.recipient, text=self.text)

        
class ListMessage(Message):
    """Client message for listing users."""
    enc_header = "LST"

    def __init__(self, wildcard=None):
        self.wildcard = wildcard

    def _data_items(self):
        """TODO: Fix when finished handling wildcard."""
        return [self.wildcard] if self.wildcard else ["*"]


class DeleteMessage(Message):
    """Client message for deleting a user."""
    enc_header = "DEL"

    def __init__(self, username):
        self.username = username

    def _data_items(self):
        return [self.username]


class QueueMessage(Message):
    """Client message for requesting queued messages.
    TODO: Should only be able to get queued messages for yourself.
    """
    enc_header = "QUE"

    def __init__(self, username):
        self.username = username


####################
### Server Messages
####################

class BroadcastMessage(Message):
    """Class for server's execution of ChatMessage requests.
    TODO: Can add metadata like when the message was sent.
    """
    enc_header = "BRO"

    def __init__(self, sender, text, direct=None):
        """
        Initialize BroadcastMessage.

        Args:
            sender (str): The username of the sender.
            text (str): The text of the chat message.
            direct (str): The username of the recipient if direct message, else None.
        """
        self.sender = sender
        self.text = text
        self.direct = direct

    def _data_items(self):
        # If `direct` is None, represent with empty string
        direct_str = self.direct if self.direct else "" 
        return [self.sender, direct_str, self.text]
    

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
    """
    Response format for registering username. Extends Response class with
    a boolean that is False if the user is a returning user, i.e. the username
    has previously been registered.
    """
    enc_header = "RESR"

    def __init__(self, success, error=None, is_new_user=None):
        super().__init__(success, error)
        self.is_new_user = is_new_user

    def _data_items(self):
        # If `is_new_user` is None, it is an error response. Include an empty
        # string in place of this field.
        new_user_str = str(int(self.is_new_user)) if self.is_new_user != None else ""
        return super()._data_items() + [new_user_str]
    
    
class ChatResponse(Response):
    """Response format for chat messages."""
    enc_header = "RESC"


class ListResponse(Response):
    """
    Response format for ListMessage. Extends Response class to 
    include sending the list of users.
    """
    enc_header = "RESL"

    def __init__(self, success, users, error=None):
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


class QueueResponse(Response):
    """Response for requesting queued messages. The actual messages
    are sent separately."""
    enc_header = "RESQ"


def encode_msg_queue(msgs):
    """
    Function that takes a list of BroadcastMessage instances and returns
    a list of byte strings, where each string is at most MAX_BUFFER_SIZE.

    Args:
        msgs (List[BroadcastMessage]): The queued messages.

    Returns:
        List[byte str]
    """
    # List of byte strings 
    out = []

    data = b""
    for msg in msgs:
        # Add the encoded byte string to 
        encoded = msg.encode_()
        # Check that adding message doesn't exceed MAX_BUFFER_SIZE
        if len(encoded) + len(data) < MAX_BUFFER_SIZE:
            data += encoded
        # Otherwise append `data` and start a new byte string
        else:
            out.append(data)
            data = encoded

    # Append remaining data
    if data:
        out.append(data)
        
    return out


####################
### Decoding
####################

def _deserialize_client_message(msg):
    """
    Factory method for deserializing a message string to appropriate Message subclass.
    
    Args:
        msg (str): The decoded string.
    
    Returns:
        Message: The deserialized Message instance.
    """
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
    elif content[0] == QueueMessage.enc_header:
        return QueueMessage(username=content[1])
    else:
      raise ValueError("Unknown message type header received from client.")


def _deserialize_server_message(msg):
    """
    Factory method for deserializing a message string to appropriate Message subclass.
    
    Args:
        msg (str): The decoded string.
    
    Returns:
        Message: The deserialized Message instance.
    """
    content = msg.split(Message.separator_token)

    if content[0] == RegisterResponse.enc_header:
        return RegisterResponse(success=bool(int(content[1])), error=content[2], is_new_user=content[3])
    elif content[0] == ChatResponse.enc_header:
        return ChatResponse(success=bool(int(content[1])), error=content[2])
    elif content[0] == DeleteResponse.enc_header:
        return DeleteResponse(success=bool(int(content[1])), error=content[2])
    elif content[0] == ListResponse.enc_header:
        users = content[3:] if len(content) > 2 else None
        return ListResponse(success=bool(int(content[1])), error=content[2], users=users)
    elif content[0] == BroadcastMessage.enc_header:
        direct = content[2] if content[2] != "" else None
        return BroadcastMessage(sender=content[1], direct=direct, text=content[3])
    elif content[0] == QueueResponse.enc_header:
        return QueueResponse(success=bool(int(content[1])), error=content[2])
    else:
        raise ValueError("Unknown message type header received from server.")
    

def _decode_buffer(deserialize_fn):
    """
    Closure for decoding byte buffers with a given deserialization function. The returned
    function splits the buffer into individual messages, and then applies the deserialization
    function to each.

    NOTE: Messages that cannot be deserialized are ignored.

    Args: 
        deserialization_fn (str -> Message): A function that converts a decoded string
            into a Message instance.
    
    Returns:
        (buffer -> List[Message]): A function that decodes a buffer into a list of
            messages.
    """
    def inner(buffer):
        decoded_str = buffer.decode()
        msgs = decoded_str.split(Message.EOM_token)

        # If we have received a sequence of valid messages, the last token
        # should be EOM_token, so the last item returned by `split()` should
        # be "". Otherwise, ignore the incomplete message.
        if msgs[-1] != "":
            logging.warning("The buffer did not end with a complete message. Ignoring last message.")
        msgs = msgs[:-1]

        # Loop through messages and try to decode, ignoring if decoding fails
        out = []
        for msg in msgs:
            try:
                decoded = deserialize_fn(msg)
            except ValueError as e:
                logging.error(f"Could not decode message {msg}: {e}")
            else:
                out.append(decoded)
        
        return out

    return inner


# Function for decoding a buffer on the client side
decode_client_buffer = _decode_buffer(_deserialize_client_message)


# Function for decoding a buffer on the server side
decode_server_buffer = _decode_buffer(_deserialize_server_message)




"""
Defines message schema.
TODO: Probably want to have the conversion to bytes handled better.
TODO: Refactor shared components.
TODO: We could separate out the code for client and server messages, but not sure it's necessary.
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
        return BroadcastMessage(text=self.text)

        
class ListMessage(Message):
    enc_header = "LIST"

    def __init__(self, wildcard):
        self.wildcard = wildcard

    def encode_(self):
        out_str = self.separator_token.join([self.enc_header, self.wildcard])
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

class ResponseMessage(Message):
    """
    TODO: We may want to refactor this into a class for response to each kind of message.
    """
    enc_header = "RES"

    def __init__(self, success, error=None):
        self.success = success # 1 is true, 0 is false
        self.error = error if error else ""

    def encode_(self):
        out_str = self.separator_token.join([self.enc_header, str(self.success), self.error])
        return out_str.encode()


class BroadcastMessage(Message):
    """Class for server's execution of ChatMessage requests.
    TODO: Can add metadata like when the message was sent.
    """
    enc_header = "BROAD"

    def __init__(self, text):
        self.text = text

    def encode_(self):
        out_str = self.separator_token.join([self.enc_header, self.text])
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
        return ListMessage(wildcard=content[1])
    elif content[0] == DeleteMessage.enc_header:
        return DeleteMessage(username=content[1])
    else:
      raise ValueError("Unknown message type header received from client.")


def decode_server_message(msg):
    """Factory method for converting read buffer data on client side to appropriate Message subclass."""
    msg = msg.decode() # Need to convert back to string
    content = msg.split(Message.separator_token)
    if content[0] == ResponseMessage.enc_header:
        return ResponseMessage(success=content[1], error=content[2])
    elif content[0] == BroadcastMessage.enc_header:
        return BroadcastMessage(text=content[1])
    else:
        raise ValueError("Unknown message type header received from server.")
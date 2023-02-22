"""
Python program to implement client side of chat application.

TODO: Input should be cleared of separator token, otherwise that 
will mess up message.
"""
import socketx
import select
import sys
import logging

from .protocol import *
from .config import config


# Logging
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)


# Configuration
DEBUG = config["DEBUG"]
MAX_BUFFER_SIZE = config["MAX_BUFFER_SIZE"]
SERVER_ADDRESS = config["SERVER_ADDRESS"] if not DEBUG else config["DEBUG_SERVER_ADDRESS"]
SERVER_PORT = config["SERVER_PORT"]


def _authenticate(server):
    """
    This will hold the client at sending `REGISTER` messages until a
    success response is received, then returns the client's
    username and whether they are a previous user. Other messages from the server will be
    ignored.

    Args:
        server (Socket): The socket to send register message to.

    Returns:
        Tuple[str, bool]: The first argument is the username, and the
            second argument is whether the user is new or returning.

    Raises:
        ConnectionError: If the server disconnects during the process or a RegisterResponse
            is not received.
    """
    while True:
        username = input("Enter your username:")
        msg = RegisterMessage(username=username)
        server.send(msg.encode_())

        # Now listen for the desired success/error response, other messages
        # from server will be ignored.
        while True:
            res = server.recv(MAX_BUFFER_SIZE)
            # If no bytes received, server has disconnected
            if not res:
                raise ConnectionError("Server has disconnected.")
            
            # Since the buffer could contain multiple messages, ignore 
            # all messages except the last RegisterResponse
            msgs = decode_server_buffer(res)
            res = None
            for msg in msgs:
                if isinstance(msg, RegisterResponse):
                    res = msg
            
            # If no RegisterResponse was recieved, something went wrong, raise ConnectionError
            if not res:
                raise ConnectionError()
            # If success response, return the username for future use
            if res.success:
                return username, res.is_new_user
            # Otherwise, display the error message and wait for user input
            else:
                print(res.error)
                break
        

def _display_message(msg):
    """
    Display message on the client console. The formatting depends on the instance of 
    Message.

    NOTE: Use this to modify formatting for messages, e.g. adding time, colors, etc.
    See `client_ex.py` for an example of this.

    Args:
        msg (Message): A Message instance received from server.
    
    Returns:
        None
    """
    if isinstance(msg, BroadcastMessage):
        # Different formating for direct messages
        if msg.direct:
            print(f"{msg.sender}>>{msg.direct}: {msg.text}")
        else:
            print(f"{msg.sender}: {msg.text}")
    elif isinstance(msg, ListResponse):
        # If the `limit_exceeded` flag is True, let the user know
        # that there are users that satisfy wildcard.
        if msg.limit_exceeded:
            print(f"There are more users satisfying this query. Only showing the first {msg.max_num_users}")
        for username in msg.users:
            print(username)
    elif isinstance(msg, DeleteResponse):
        if not msg.success:
            print(msg.error)
        else:
            print("Successfully deleted user.")
    # Handle other error responses
    elif isinstance(msg, Response):
        # If it's an error response, print the error
        if not msg.success:
            print(f"Error: {msg.error}")
    else:
        raise NotImplementedError


def _display_usage_instructions():
    """Print the usage instructions."""
    print("(1) Send a message to all --> type message and press enter")
    print("(2) Send a message to specified recipient --> '>> [recipient]: [message]'")
    print("(3) List all recipients w/ optional wildcard --> '/list [wildcard]'")
    print("(4) Delete a specified recipient account --> '/delete [recipient]'")
    print("(5) Get messages in your queue --> '/queue'")
    print("(6) Logout --> '/logout'")


def _message_from_input(input, username):
    """
    Convert the user input into a Message object.
    
    Args:
        input (str): The input read from sys.stind.
        username (str): The username of client.

    Returns:
        Message: The message to send to server.

    Raises:
        ValueError: If the message cannot be encoded as a Message instance.
    """
    try:
        # Strip leading and ending whitespace
        input = input.strip()
        if input.startswith("/list"):
            fields = input.split(" ")
            # If input is just `/list`, wildcard is None
            wildcard = fields[1] if len(fields) > 1 else None
            return ListMessage(wildcard=wildcard)
        elif input.startswith("/delete"):
            return DeleteMessage(username=input.split(" ")[1])
        elif input.startswith("/queue"):
            return QueueMessage(username=username)
        # User requesting to send a direct message to a specified recipient
        elif input.startswith(">>"):
            fields = input.split(":")
            recipient = fields[0].replace(">", "").strip()
            text = fields[1].strip()
            return ChatMessage(sender=username, recipient=recipient, text=text)
        else:
            return ChatMessage(sender=username, text=input)
    except Exception as e:
        raise ValueError(str(e))


def run(ip_address, port):
    """
    The control logic for client connection. First calls `_authenticate`, which
    blocks until a valid username is registered. Then continuously reads from server socket
    and `sys.stind`, displaying messages from the server and sending messages to the server, respectively.
    This loop continues until either the server disconnects or the user inputs "/logout".
    """
    # Initialize TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        # Initialize connection with server
        server.connect((ip_address, port))

        # _authenticate will loop until a username is successfully registered
        # If the server disconnects during this process, it will raise ConnectionError
        try:
            username, is_new_user = _authenticate(server)
        except ConnectionError as _:
            print("Server disconnected.")
            server.close()
            return

        # Print different messages depending on if new user
        if is_new_user:
            print(f"Welcome to the chatroom {username}!")
        else:
            print(f"Welcome back {username}!")

        # Print usage instructions
        _display_usage_instructions()        

        while True:
            # Maintain a list of possible input streams
            sockets_list = [sys.stdin, server]
            read_sockets, _, _ = select.select(sockets_list,[],[])
        
            for socks in read_sockets:
                # If the read buffer from server has data, decode and display
                if socks == server:
                    data = socks.recv(MAX_BUFFER_SIZE)
                    if data:
                        msgs = decode_server_buffer(data)
                        # Iterate through the received messages and display
                        for msg in msgs:
                            _display_message(msg)
                    # If 0 bytes are recieved, the server has disconnected
                    else:
                        print("Server disconnected.")
                        server.close()
                        return
                # If the client console has input, convert to a Message instance and send to server
                else:
                    input = sys.stdin.readline()
                    # Exit if the input is `/logout`
                    if input.startswith("/logout"):
                        print("Logging out.")
                        server.close()
                        return
                    # Try to cast user input to a message. If this fails,
                    # print a message explaining how to use.
                    try:
                        msg = _message_from_input(input, username)
                        server.send(msg.encode_())
                    except ValueError as _:
                        print("Improper usage.")
                        _display_usage_instructions()


if __name__ == "__main__":
    # Run client with the specified server address and port
    run(SERVER_ADDRESS, SERVER_PORT)
"""
Python program to implement client side of chat application.

TODO: Refactor to make cleaner.
TODO: Better control, right now control flow is quite messy, e.g. using
`return` to exit out of some loops. Maybe use `exit()` instead?
TODO: Might want to use a thread for listening as in `client_ex.py`.
TODO: Add a way for client to gracefully exit, e.g. "/quit".
"""
import socket
import select
import sys
import logging

from protocol import *
from config import config


# Logging
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)


# Configuration
MAX_BUFFER_SIZE = config["MAX_BUFFER_SIZE"]
SERVER_ADDRESS = config["SERVER_ADDRESS"]
SERVER_PORT = config["SERVER_PORT"]


def _authenticate(server):
    """
    This will hold the client at sending `REGISTER` messages until a
    success response is received, then returned the client's
    username. Other messages from the server will be
    ignored.

    TODO: Might want to refactor, unsure about the nested while loops.
    TODO: What other messages could be expected? Depends on behavior we want for
    unauthenticated clients.

    Args:
        server (Socket): The socket to send register message to.

    Returns:
        Tuple[str, bool]: The first argument is the username, and the
            second argument is whether the user is new or returning.
    """
    while True:
        username = input("Enter your username:")
        msg = RegisterMessage(username=username)
        server.send(msg.encode_())

        # Now listen for the desired success/error response. Other messages
        # from server will be ignored. 
        while True:
            res = server.recv(MAX_BUFFER_SIZE)
            # If no bytes received, server has disconnected
            if not res:
                raise ConnectionError("Server has disconnected.")
            res = decode_server_buffer(res)

            # TODO: Right now we just assume that there is only one message
            assert len(res) == 1
            res = res[0]
            
            # If success response, return the username for future use
            if res.success:
                return username, res.is_new_user
            else:
                print(res.error)
                break
        

def _display_message(msg):
    """
    Display message on the client console.
    NOTE: Use this to modify formatting for messages, e.g. adding time, colors, etc.
    See `client_ex.py` for an example of this.
    TODO: I think the format should look different

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
        for username in msg.users:
            print(username)
    elif isinstance(msg, DeleteResponse):
        if not msg.success:
            print(msg.error)
        else:
            print("Successfully deleted user.")
    # This handles other error responses, but we shouldn't get any
    elif isinstance(msg, Response):
        # If it's an error response, print the error
        if not msg.success:
            print(f"Error: {msg.error}")
    else:
        raise NotImplementedError


def _message_from_input(input, username):
    """
    Convert the user input into a Message object.
    TODO: Cleaner handling of converting input to message data, e.g. strip whitespace.
    
    Args:
        input (str): The input read from sys.stind.
        username (str): The username of client.

    Returns:
        Message: The message to send to server.
    """
    if input.startswith("/list"):
        if len(input.split(" ")) == 1:
            wildcard = None
        else:
            wildcard = input.split(" ")[1]
        return ListMessage(wildcard=wildcard)
    elif input.startswith("/delete"):
        input = input.strip()
        return DeleteMessage(username=input.split(" ")[1])
    elif input.startswith("/queue"):
        input = input.strip()
        return QueueMessage(username=input.split(" ")[1])
    # user requesting to send a direct message to a specified recipient
    elif input.startswith(">>"):
        msgList = input.split(":")
        usernameToSend1 = msgList[0].replace(">", "")
        usernameToSend = usernameToSend1.replace(" ", "")
        msgText = msgList[1]
        return ChatMessage(sender=username, recipient=usernameToSend, text=msgText)
    else:
        return ChatMessage(sender=username, text=input)


def run(IP_address, port):
    # Initialize TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        # Initialize connection with server
        server.connect((IP_address, port)) # TODO: Handle exceptions

        # _authenticate will loop until a username is successfully registered
        # If the server disconnects during this process, it will raise ConnectionError
        try:
            username, is_new_user = _authenticate(server)
        except ConnectionError as _:
            print("Server disconnected.")
            return

        # Print different messages depending on if new user
        if is_new_user:
            print(f"Welcome to the chatroom {username}!")
        else:
            print(f"Welcome back {username}!")

        while True:
            # TODO: Understand the use of select here.
            # Maintain a list of possible input streams
            sockets_list = [sys.stdin, server]
            read_sockets, write_socket, error_socket = select.select(sockets_list,[],[])
        
            for socks in read_sockets:
                if socks == server:
                    data = socks.recv(MAX_BUFFER_SIZE)
                    if data:
                        msgs = decode_server_buffer(data)
                        # Iterate through the received messages and display
                        for msg in msgs:
                            _display_message(msg)
                    # If there is no data received, stop listening
                    else:
                        print("Server disconnected.")
                        return
                else:
                    input = sys.stdin.readline()
                    msg = _message_from_input(input, username)
                    server.send(msg.encode_())


if __name__ == "__main__":
    # parse and check arguments
    # TODO: Add defaults and better input handling
    # if len(sys.argv) != 4:
    #     print ("Correct usage: script, IP address, port number")
    #     exit()
    # IP_address = str(sys.argv[1])
    # port = int(sys.argv[2])
    IP_address = SERVER_ADDRESS
    port = SERVER_PORT # server's port

    run(IP_address, port)
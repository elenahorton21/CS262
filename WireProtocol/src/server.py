"""
Implementation of server for chat application.

TODO: Wondering if we need to nest every interaction with AppState
in a function that uses locks.
"""
import socket
from threading import Thread, Lock
import logging

from protocol import *
from config import config
from app import AppState


# Logging config
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)


# Server config
SERVER_HOST = config["SERVER_HOST"]
SERVER_PORT = config["SERVER_PORT"]
MAX_BUFFER_SIZE = config["MAX_BUFFER_SIZE"]
MAX_NUM_CONNECTIONS = config["MAX_NUM_CONNECTIONS"]


# initialize list/set of all connected client's sockets
client_sockets = set()
# create a TCP socket
s = socket.socket()
# make the port as reusable port
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# bind the socket to the address we specified
s.bind((SERVER_HOST, SERVER_PORT))
# listen for upcoming connections
s.listen(MAX_NUM_CONNECTIONS)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

# Initialize app state
app = AppState() # TODO: Change name


def _broadcast_to_all(msg, app):
    """
    Send a message to all active users. Ignores connections that haven't 
    registed a username.

    Args:
        msg (BroadcastMessage): The message to send.
        app (AppState): The current app state, which includes active user info.

    Returns:
        None
    """
    # Check that the message is an instance of BroadcastMessage
    assert isinstance(msg, BroadcastMessage)

    recv_conns = app.get_all_connections()
    encoded_msg = msg.encode_()
    for conn in recv_conns:
        conn.send(encoded_msg)


def _handle_chat_message(msg, app, socket):
    """
    Receives a ChatMessage. Returns an error response if the recipient
    does not exist. Queues the message if recipient is not active. Otherwise
    broadcast to recipient (or all if recipient is None).
    
    TODO: Right now this only sends a ChatResponse if the username does not exist.
    Does not send success responses.

    Args:
        msg (ChatMessage): The message received from client.
        app (AppState)
        socket (Socket): The socket that server received message from.
    
    Returns:
        None
    """
    # If recipient was not specified, broadcast to all active users
    if not msg.recipient:
        broadcast_msg = msg.to_broadcast()
        # TODO: Should we send a success response back to the sender?
        _broadcast_to_all(broadcast_msg, app)

    # If the user does not exist, return an error response to sender
    elif not app.is_valid_user(msg.recipient):
        res = RegisterResponse(success=False, error="User does not exist.")
        socket.send(res.encode_())

    # If the recipient exists and is active, send the message to their socket.
    # Otherwise add the message to their message queue.
    else:
        recv_conn = app.get_user_connection(msg.recipient) # Returns None if no active connection
        if not recv_conn:
            app.queue_message(msg.recipient, msg.to_broadcast())
        else:
            # Send the message to both sender and recipient
            recv_conns = [recv_conn, socket]
            encoded_msg = msg.to_broadcast().encode_()
            for conn in recv_conns:
                conn.send(encoded_msg)


def _handle_register_message(msg, app, socket):
    try:
        is_existing = app.add_connection(msg.username, socket)
    except ValueError as e:
        print(e)
        res = RegisterResponse(success=False, error=str(e))
        socket.send(res.encode_())
    else:
        res = RegisterResponse(success=True)
        socket.send(res.encode_())
        # If existing user, check if we need to send msg queue
        # TODO: Test that this works properly.
        if is_existing and msg.username in app.msg_queue:
            # TODO: Should delete the corresponding messages once they are delivered
            for msg in app.msg_queue[msg.username]:
                socket.send(msg.encode_())


def _handle_list_message(msg, app, socket):
    """
    Handle ListMessage.
    TODO: Change to wildcard functionality. Right now this just lists all users.
    """
    users = app.list_users()
    res = ListResponse(success=True, users=users)
    socket.send(res.encode_())


def _handle_delete_message(msg, app, socket):
    """Handle DeleteMessage.
    TODO: Does not handle the case where the user is connected.
    """
    if not app.is_valid_user(msg.user):
        res = DeleteResponse(success=False, error="User does not exist.")
        socket.send(res.encode_())
    else:
        app.delete_user(msg.user)
        res = DeleteResponse(success=True)
        socket.send(res.encode_())


def handle_message(msg, app, socket):
    logging.debug(f"Handling message from {socket.getsockname()}")

    # Try to decode message. If this fails, return an error response.
    try:
        msg = decode_client_message(msg)
    except ValueError as e:
        # TODO: Unsure if we should be sending a response, or just
        # ignoring messages that can't be decoded.
        res = Response(success=False, error=str(e))
        socket.send(res.encode_())
    else:
        if isinstance(msg, RegisterMessage):
            _handle_register_message(msg, app, socket)
        elif isinstance(msg, ChatMessage):
            _handle_chat_message(msg, app, socket)
        elif isinstance(msg, ListMessage):
            _handle_list_message(msg, app, socket)
        elif isinstance(msg, DeleteMessage):
            _handle_delete_message(msg, app, socket)
        else:
            raise NotImplementedError


def _disconnect_client(socket, app):
    """Remove the socket from active connections in app state."""
    client_sockets.remove(socket)
    app.remove_connection(socket)
    print(f"Removed {socket.getsockname()}")


def client_thread(cs, app_state):
    """
    This function keep listening for a message from `cs` socket
    TODO: Handle disconnected clients.
    """
    while True:
        try:
            # keep listening for a message from `cs` socket
            buffer = cs.recv(MAX_BUFFER_SIZE)
            if not buffer:
                # This should only happen if client disconnects
                logging.debug("Received 0 bytes from socket.")
                _disconnect_client(cs, app_state)
                return
            else:
                handle_message(buffer, app_state, cs)
        except Exception as e:
            # TODO: What exceptions could we get here?
            print(f"[!] Error: {e}")
            return
            # _disconnect_client(cs, app_state)


while True:
    # Listen for new connections to accept
    client_socket, client_address = s.accept()
    logging.info(f"{client_address} has connected.")
    # Add the new client to connected sockets
    client_sockets.add(client_socket)
    # Create a thread for each client
    t = Thread(target=client_thread, args=(client_socket, app))
    # Make the thread a daemon so it ends when the main thread does
    t.daemon = True
    # Start the thread
    t.start()


# close client sockets
for cs in client_sockets:
    cs.close()
# close server socket
s.close()
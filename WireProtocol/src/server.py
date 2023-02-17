"""
Implementation of server for chat application.

TODO: Move socket out of handle functions, handle functions instead return
response.
TODO: Create a broadcast function.
"""
import socket
from threading import Thread
import logging

from protocol import *
from config import config
from app import AppState, InvalidUserError


# Logging config
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)


# Server config
SERVER_HOST = config["SERVER_HOST"]
SERVER_PORT = config["SERVER_PORT"]
MAX_BUFFER_SIZE = config["MAX_BUFFER_SIZE"]
MAX_NUM_CONNECTIONS = config["MAX_NUM_CONNECTIONS"]


# Initialize set of all connections
client_sockets = set()
# Create a TCP socket
s = socket.socket()
# Make the port reusable
# TODO: Should we change this when working with multiple devices?
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Bind the socket
s.bind((SERVER_HOST, SERVER_PORT))
# Listen for connections
s.listen(MAX_NUM_CONNECTIONS)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

# Initialize app state
app = AppState() 


def broadcast(msg, recvs):
    """
    Send a message to a list of clients.
    TODO: Handle exceptions with `conn.send`.

    Args:
        msg (BroadcastMessage): The message to send to clients.
        recvs (List[Socket]): The sockets to send the message to.

    Returns:
        None
    """
    # Check that the message is an instance of BroadcastMessage
    assert isinstance(msg, BroadcastMessage)

    for conn in recvs:
        conn.send(msg.encode_())


def _handle_register_message(msg, app, socket):
    """
    Handle a RegisterMessage from client.
    TODO: This no longer handles delivering queued messages.
    """
    try:
        is_existing = app.add_connection(msg.username, socket)
    except ValueError as e:
        logging.debug(f"Cannot register username: {e}")
        res = RegisterResponse(success=False, error=str(e))
    else:
        res = RegisterResponse(success=True)
    finally:
        return res


def _handle_chat_message(msg, app):
    """
    Handle a ChatMessage from client. Returns an error response if the recipient
    does not exist. Otherwise, broadcasts to active recipients, queues the 
    the message for inactive recipients, and returns a success response.

    Args:
        msg (ChatMessage): The message received from client.
        app (AppState): The current app state.
    
    Returns:
        ChatResponse: The response to client.
    """
    # If the recipient does not exist, return an error response
    if msg.recipient and not app.is_valid_user(msg.recipient):
        res = ChatResponse(success=False, error="User does not exist.")
        return res

    # Convert ChatMessage to BroadcastMessage
    broadcast_msg = msg.to_broadcast() 
    # If recipient was not specified, all active users are recipients
    if not msg.recipient:
        recv_conns = app.get_all_connections()
    # Otherwise, broadcast the message to sender, and recipient if active.
    else:
        # TODO: Roundabout way of getting sender socket    
        recv_conns = [app.get_user_connection(msg.sender)]
        # Get recipient socket
        recipient_conn = app.get_user_connection(msg.recipient)
        # If recipient is active, add their socket to receiving connections
        if recipient_conn:
            recv_conns.append(recipient_conn)
        # If `recv_conn` is None, the user is inactive. Queue the message for later.
        else:
            app.queue_message(msg.recipient, broadcast_msg)
    
    # Broadcast the message to recipients
    # TODO: Are there cases where this fails and we should return error response?
    broadcast(broadcast_msg, recv_conns)

    # Return success response
    return ChatResponse(success=True)


def _handle_list_message(msg, app):
    """
    Handle ListMessage.
    TODO: Change to wildcard functionality. Right now this just lists all users.
    """
    users = app.list_users(wildcard=msg.wildcard)
    res = ListResponse(success=True, users=users)
    return res


def _handle_delete_message(msg, app):
    """
    Handle DeleteMessage from client. Will return an error response if
    the username does not exist, or if the user is active.

    Args:
        msg (DeleteMessage): The delete message from client.
        app (AppState): The app state.

    Returns:
        DeleteResponse: Response to send to client.
    """
    try:
        app.delete_user(msg.username)
    except InvalidUserError as e:
        res = DeleteResponse(success=False, error=str(e))
    except ValueError as e2:
        res = DeleteResponse(success=False, error=str(e2))
    else:
        logging.info(f"User {msg.username} deleted.")
        res = DeleteResponse(success=True)
    finally:
        return res


def handle_message(msg, app, socket):
    """
    Returns:
        Response
    """
    logging.debug(f"Handling message from {socket.getsockname()}")

    # Try to decode message. If this fails, return an error response.
    try:
        msg = decode_client_message(msg)
    except ValueError as e:
        # TODO: Unsure if we should be sending a response, or just
        # ignoring messages that can't be decoded.
        res = Response(success=False, error=str(e))
        return res
    else:
        # TODO: For now, `_handle_register_message` needs
        # to be passed the socket to register the connection. 
        if isinstance(msg, RegisterMessage):
            return _handle_register_message(msg, app, socket)
        elif isinstance(msg, ChatMessage):
            return _handle_chat_message(msg, app)
        elif isinstance(msg, ListMessage):
            return _handle_list_message(msg, app)
        elif isinstance(msg, DeleteMessage):
            return _handle_delete_message(msg, app)
        else:
            raise NotImplementedError


def _disconnect_client(socket, app):
    """Remove the socket from active connections in app state."""
    client_sockets.remove(socket)
    app.remove_connection(socket)
    logging.info(f"Removed {socket.getsockname()}")


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
                # Handle message and return response to client
                res = handle_message(buffer, app_state, cs)
                # Send the response in byte format
                cs.send(res.encode_())
        except Exception as e:
            # TODO: What exceptions could we get here?
            print(f"[!] Error: {e}")
            _disconnect_client(cs, app_state)
            return


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
"""
Implementation of server for chat application.
"""
import socket
from threading import Thread
import logging

from .protocol import *
from .config import config
from .app import AppState, InvalidUserError


# Logging config
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)


# Server config
SERVER_HOST = config["SERVER_HOST"]
SERVER_PORT = config["SERVER_PORT"]
MAX_BUFFER_SIZE = config["MAX_BUFFER_SIZE"]
MAX_NUM_CONNECTIONS = config["MAX_NUM_CONNECTIONS"]


def broadcast(msg, recvs):
    """
    Broadcast a message to a list of clients.

    Args:
        msg (BroadcastMessage): The message to send to clients.
        recvs (List[Socket]): The sockets to send the message to.

    Returns:
        None
    """
    # Check that the message is an instance of BroadcastMessage
    if not isinstance(msg, BroadcastMessage):
        raise TypeError("Server can only broadcast BroadcastMessage objects.")

    for conn in recvs:
        conn.send(msg.encode_())


def register_service(msg, app):
    """
    Service for handling register messages from client. Returns an
    error response if the username is currently being used or the 
    username contains non-alphanumeric characters. Otherwise return a
    success response where `is_new_user` field is false if the username
    has previously been registered.

    Args:
        msg (ChatMessage): The message received from client.
        app (AppState): The current app state.
    
    Returns:
        ChatResponse: The response to client.        
    """
    try:
        is_new_user = app.register_user(msg.username)
    except InvalidUserError as e:
        logging.debug(f"Cannot register username '{msg.username}': {e}")
        res = RegisterResponse(success=False, error=str(e))
    except ValueError as e:
        logging.debug(f"Cannot register username '{msg.username}': {e}")
        res = RegisterResponse(success=False, error=str(e))
    else:
        res = RegisterResponse(success=True, is_new_user=is_new_user)
    finally:
        return res


def chat_service(msg, app):
    """
    Service for handling a ChatMessage from client. Returns an error response if the recipient
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
        # Roundabout way of getting sender socket    
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
    broadcast(broadcast_msg, recv_conns)

    # Return success response
    return ChatResponse(success=True)


def list_service(msg, app):
    """
    Service for handling ListMessage. Will match the wildcard as a regex
    expression, or return all users if wildcard is None. If there are more
    users that match the wildcard than the limit, only send the first `max_num_users` 
    usernames and set the `limit_exceeded` flag to True so the client knows that the 
    list is incomplete.

    Args:
        msg (ListMessage): The message from client.
        app (AppState): The app state.

    Returns:
        ListResponse: The response to send to client.
    """
    users = app.list_users(wildcard=msg.wildcard)
    # Only return up to `max_num_users` users in response
    # Flag lets the client know that there are more users
    if len(users) > ListResponse.max_num_users:
        users = users[:ListResponse.max_num_users]
        res = ListResponse(success=True, users=users, limit_exceeded=True)
    else:
        res = ListResponse(success=True, users=users)
    return res


def delete_service(msg, app):
    """
    Service for handling DeleteMessage from client. Will return an error response if
    the username does not exist or the user is active.

    Args:
        msg (DeleteMessage): The delete message from client.
        app (AppState): The app state.

    Returns:
        DeleteResponse: Response to send to client.
    """
    try:
        app.delete_user(msg.username)
    # InvalidUserError is raised if username is not registered
    except InvalidUserError as e:
        res = DeleteResponse(success=False, error=str(e))
    # ValueError is raised if the user is active
    except ValueError as e2:
        res = DeleteResponse(success=False, error=str(e2))
    else:
        logging.info(f"User {msg.username} deleted.")
        res = DeleteResponse(success=True)
    finally:
        return res


def queue_service(msg, app):
    """
    Service for delivering queued messages to a user. If there are queued messages,
    send them as BroadcastMessages, making sure that each `cs.send()` call is passed a 
    byte string smaller than `MAX_BUFFER_SIZE`, and then return a success response.
    Otherwise, return an error response.

    Args:
        msg (QueueMessage): The message from client containing the user to get queued messages for.
        app (AppState): The current app state.
    
    Returns:
        QueueResponse: True if there are messages in the queue, False otherwise.
    """
    queued_msgs = app.get_queued_messages(msg.username)

    # If no messages, return error response
    if not queued_msgs:
        return QueueResponse(success=False, error="No messages in queue.")
    
    # Roundabout way of getting client socket
    cs = app.get_user_connection(msg.username)

    # Encode the messages into concantenated byte strings with max length
    for data in encode_msg_queue(queued_msgs):
        cs.send(data)

    return QueueResponse(success=True)


def handle_message(msg, app, socket):
    """
    Route a Message instance to the appropriate service.

    Args:
        msg (str): The string to be deserialized.
        app (AppState): The app state.
        socket (Socket): The client socket that sent message.

    Returns:
        Response: The response to send to client.

    Raises:
        NotImplementedError: If there is no service for handling the type of the Message instance.
    """
    logging.debug(f"Handling message from {socket.getsockname()}")

    if isinstance(msg, RegisterMessage):
        res = register_service(msg, app)
        # If the response is a successful register response,
        # add the current socket as the user's socket
        if res.success:
            app.add_connection(msg.username, socket)
    elif isinstance(msg, ChatMessage):
        res = chat_service(msg, app)
    elif isinstance(msg, ListMessage):
        res = list_service(msg, app)
    elif isinstance(msg, DeleteMessage):
        res = delete_service(msg, app)
    elif isinstance(msg, QueueMessage):
        res = queue_service(msg, app)
    else:
        raise NotImplementedError
    
    return res


def disconnect_client(socket, app):
    """
    Handle a disconnected client. Remove it from active connections in 
    app state, and close the socket.

    Args:
        socket (Socket): The client to remove.
        app (AppState): The app state.

    Returns:
        None
    """
    logging.info(f"Removing {socket.getsockname()}")
    # Remove the socket from active connections in app state
    app.remove_connection(socket)
    socket.close()


def client_thread(cs, app):
    """
    This function keeps listening for a message from `cs` socket.
    If data is received, decode the buffer into one or more Message
    instances, pass them to them appropriate service, and send response
    back to client. If the client has disconnnected, remove them from 
    active connections and app state.

    Args:
        cs (Socket): The socket to listen to.
        app (AppState): The app state.

    Returns:
        None
    """
    while True:
        try:
            # Listen for a message from `cs` socket
            buffer = cs.recv(MAX_BUFFER_SIZE)
        except Exception as e:
            logging.error(f"[!] Error: {e}")
            disconnect_client(cs, app)
        else:
            # If buffer is 0, the client has disconnected
            if not buffer:
                logging.debug("Received 0 bytes from socket.")
                disconnect_client(cs, app)
                return
            # Otherwise, decode the buffer and handle each message
            else:
                msgs = decode_client_buffer(buffer)
                for msg in msgs:
                    # Handle message and return response to client
                    res = handle_message(msg, app, cs)
                    # Send the response in byte format
                    cs.send(res.encode_())


if __name__ == "__main__":
    """
    Sets up the server socket and listens for connections. For each client that connects,
    create a daemon thread that handles messages from the socket. `app_state` is shared between
    all threads.
    """
    # Create a TCP socket
    s = socket.socket()
    # Make the port reusable
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the socket
    s.bind((SERVER_HOST, SERVER_PORT))
    # Listen for connections
    s.listen(MAX_NUM_CONNECTIONS)
    print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

    # Initialize app state
    app_state = AppState() 

    while True:
        # Listen for new connections to accept
        client_socket, client_address = s.accept()
        logging.info(f"{client_address} has connected.")
        # Create a thread for each client
        t = Thread(target=client_thread, args=(client_socket, app_state))
        # Make the thread a daemon so it ends when the main thread does
        t.daemon = True
        # Start the thread
        t.start()
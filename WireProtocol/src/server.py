import socket
from threading import Thread, Lock
import logging

from protocol import *
from config import config
from app import AppState as ChatApp


# Logging config
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)


# Server config
SERVER_HOST = config["SERVER_HOST"]
SERVER_PORT = config["SERVER_PORT"]
MAX_BUFFER_SIZE = config["MAX_BUFFER_SIZE"]


# initialize list/set of all connected client's sockets
client_sockets = set()
# create a TCP socket
s = socket.socket()
# make the port as reusable port
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# bind the socket to the address we specified
s.bind((SERVER_HOST, SERVER_PORT))
# listen for upcoming connections
s.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

# Initialize app state
app = ChatApp()

def handle_message(msg, app, socket):    
    if isinstance(msg, RegisterMessage):
        try:
            is_existing = app.add_connection(msg.username, socket)
        except ValueError as e:
            print(e)
            res = ResponseMessage(success=0, error= str(e))
            socket.send(res.encode_())
        else:
            res = ResponseMessage(success=1)
            socket.send(res.encode_())
            # If existing user, check if we need to send msg queue
            if is_existing and msg.username in app.msg_queue:
                for msg in app.msg_queue[msg.username]:
                    socket.send(msg.encode_())
        

    elif isinstance(msg, ChatMessage):
        # TODO: Need a special symbol for `TO ALL` that can't be a username
        # TODO: Do we need a custom function to wrap this in lock?
        # TODO: Probably want to move this logic somewhere else and clean up.
        if not msg.recipient:
            recv_conns = app.connections.values()
        else:
            # If there is no user, return an error response. 
            if msg.recipient not in app.users:
                res = ResponseMessage(success=0, error="User does not exist.")
                socket.send(res.encode_()) 
            
            # If user exists but is not logged in, add to message queue.
            #  Otherwise, deliver immediately.
            recv_conn = app.connections.get(msg.recipient, [])
            if not recv_conn:
                app.queue_message(msg.recipient, msg.to_broadcast())

            # Send to the recipient and self. If recipient is not active just send to self.
            recv_conns = recv_conn + [socket] 

        broadcast = msg.to_broadcast().encode_()
        for sock in recv_conns:
            sock.send(broadcast)


def _disconnect_client(socket, app):
    """Remove the socket from active connections in app state."""
    client_sockets.remove(socket)
    app.remove_connection(socket)


def client_thread(cs, app_state):
    """
    This function keep listening for a message from `cs` socket
    Whenever a message is received, broadcast it to all other connected clients
    TODO: Handle disconnected clients.
    """
    while True:
        try:
            # keep listening for a message from `cs` socket
            buffer = cs.recv(MAX_BUFFER_SIZE)
            msg = decode_client_message(buffer)
        except KeyError as e:
            # If the client has disconnected, remove connection
            print(f"[!] Error: {e}")
            _disconnect_client(cs, app_state)
        except ValueError as e:
            print(f"[!] Error: {e}")
            _disconnect_client(cs, app_state)
        else:
            handle_message(msg, app_state, cs)


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
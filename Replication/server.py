from concurrent import futures

import grpc
import time
import threading
import pickle
import logging

from app import App 
from config import config
import proto.chat_pb2 as chat
import proto.chat_pb2_grpc as rpc


# Logging config
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)


# Server config
SERVER_HOST = config["SERVER_HOST"]
SERVER_PORT = config["SERVER_PORT"]
REPLICA1_PORT = config["REPLICA1_PORT"]
REPLICA2_PORT = config["REPLICA2_PORT"]
MAX_BUFFER_SIZE = config["MAX_BUFFER_SIZE"]
MAX_NUM_CONNECTIONS = config["MAX_NUM_CONNECTIONS"]


class Replica:
    """Template for replica data."""
    def __init__(self, address, port):
        self.address = address
        self.port = port


# define all of the grpc functions on the server side
class ChatServer(rpc.ChatServicer):
    """
    Defines the gRPC server stubs. Also initializes intra-server communication with a server's parent replicas.
    """
    def __init__(self, parent_replicas=[], is_primary=False):
        """
        Initialize a ChatServer instance.

        Args:
            parent_replicas (List[Replica]): The replicas that this server will receive state updates from, e.g. 
                the third server has first and second server as parents.
            is_primary (bool): True if the server instance is the primary.
        """
        self.parent_replicas = parent_replicas
        self.server_id = len(parent_replicas) # Returns 0, 1, or 2
        self.is_primary = is_primary

        # This variable is used to track when the replica should yield state updates
        self.state_has_update = 0 

        # Load the application state from the replica-specific "database"
        self.app = App(load_data=True, file_path_prefix=f"db/server{self.server_id}_")

        # Create a connection for each parent replica.
        self.conns = {}
        for ind, replica in enumerate(self.parent_replicas):
            channel = grpc.insecure_channel(replica.address + ':' + str(replica.port))
            conn = rpc.ChatStub(channel)
            self.conns[ind] = conn

            # Send the timestamp and state to the primary for consensus check. This is necessary in the 
            # case that a child replica's "database" is ahead of its parents'.
            if ind == 0:
                curr_state_pkl = pickle.dumps(self.app.users)
                msg = chat.ConsensusMessage(last_modified_ts=str(self.app.last_modified_timestamp), state=curr_state_pkl)
                conn.StartupConsensus(msg)

            # Create a thread to listen to state updates from parent replicas.
            threading.Thread(target=self.__listen_for_state_updates, args=(ind,), daemon=True).start()

            # Subscribe to channel connectivity. This is an additional measure to monitor the state of the 
            # parent replicas.
            channel.subscribe(lambda event: self.__channel_connectivity_callback(event, ind))

    def __channel_connectivity_callback(self, event, conn_ind):
        """Callback function for when the channel connectivity changes with a parent replica."""
        logging.debug(f"Connectivity callback called with event {conn_ind}")

        # Remove the channel if the state is .SHUTDOWN
        if event == grpc.ChannelConnectivity.SHUTDOWN:
            print(f"Connection to server {conn_ind} ended.")
            del self.conns[conn_ind]

            # If no connections remain, set self to primary
            if not self.conns:
                self.is_primary = True

    def __listen_for_state_updates(self, conn_ind):
        """
        The `run()` function for threads that listen to state updates from parent replicas. If an 
        exception is raised, treat the parent replica as having failed and remove the connection.
        If no parent replicas remain, assume the role of primary. 

        Args:
            conn_ind (int): The index of the connection, equal to the server ID of the parent replica.

        Returns:
            None
        """
        try:
            # This will run whenever the parent replica yields a StateUpdate to StateUpdateStream
            for msg in self.conns[conn_ind].StateUpdateStream(chat.Empty()):
                logging.debug(f"Server {conn_ind} sent state update with byte length {len(msg.state)} ")
                # Set the application state to the content of the StateUpdate
                users = pickle.loads(msg.state)
                logging.debug(f"Setting app users to {users}")
                self.app.users = users
                # Save the app state to the replica's "database"
                self.app.save_state()
        except Exception as e:
            logging.info(f"Error occurred: {e}")
            # Delete the connection
            del self.conns[conn_ind]

            # If no connections remain, set self to primary
            if not self.conns:
                self.is_primary = True
                logging.info(f"Server {self.server_id} is now the primary.")

            # Exit the thread
            return

    def _handle_state_update(self):
        """
        Contains the actions to take when the server's applications state has changed. Will write 
        the changes to the server's "database" and broadcast them to the child replicas.
        """
        logging.debug("_handle_state_update called.")
        self.app.save_state()
        # This flag is used to control when the server's state should be broadcast to children
        # replicas. The initial primary will broadcast twice (once for each backup), and the 
        # first backup will broadcast once (to the second backup).
        self.state_has_update = 2 - self.server_id

    # The stream which will be used to send heartbeats to child_replica.
    def HeartbeatStream(self, request, context):
        """
        A gRPC response-streaming method that yields a heartbeat every second. This can be used
        by the child replicas to monitor when their parent replicas have died.

        NOTE: We are not currently using this because we already monitor replica state with
        the connectivity callback and by catching exceptions in the listening thread.
        """
        n = 0
        while True:
            # Only primary sends heartbeats
            if self.is_primary:
                n += 1                    
                yield chat.Heartbeat(timestamp=str(n))
            time.sleep(1)

    def StateUpdateStream(self, request, context):
        """
        A gRPC response-streaming method that yields StateUpdate messages to child replicas. Only the 
        primary will send state updates. The `state_has_update` flag is used to determine when the 
        replica's state has changed and should be broadcast.

        Args:
            request (chat.Empty): The child replica sends an empty message to start the stream.
            context: The context of the request.

        Returns:
            None
        """
        while True:
            if self.is_primary and self.state_has_update > 0:
                # Pickle app.users into bytes
                state_pkl = pickle.dumps(self.app.users)
                # Reset update flag so we don't broadcast again until state has changed
                self.state_has_update -= 1
                yield chat.StateUpdate(state=state_pkl)
    
    def StartupConsensus(self, request, context):
        """
        A gPRC stub for sending a child replica's application state to its parents. The primary can then check
        if a child replica has an application state that was modifed more recently than its own. This is necessary when 
        rebooting to ensure that the primary has the most up-to-date state.

        Args:
            request (chat.ConsensusMessage): The message from child to parent replica, which contains the child application
                state and the last modified timestamp.
            context: The context of the request.

        Returns:
            chat.Empty
        """
        if float(request.last_modified_ts) > self.app.last_modified_timestamp:
            users = pickle.loads(request.state)
            print(f"Setting app users to {users}")
            self.app = App(users=users)
            self._handle_state_update()
        
        return chat.Empty()

    def check_connection(self, request, context):
        """gRPC stub that allows the client to check if the server is down."""
        return chat.Empty()
    
    def create_user(self, request, _context):
        """
        # create a user--> 3 cases: 
        # (1) user is new, create a new account 
        # (2) user is already logged in, refuse the login. 
        # (3) user is already registered but not logged in. They are re-logged in and able to join.
        """
        username = request.username
        print("Joining user: " + username)
        result = self.app.create_user(username)
        if result == 0:
            response = "SUCCESS"
        elif result == 1:
            response = "This username is already logged in. Please choose another one."
        else:
            response = str("Welcome back " + username + " !")

        # Write the new state to "database" and broadcast to child replicas
        self._handle_state_update()

        return chat.ChatReply(message=response)

    # send message (passes to App class, which will handle either 
    # sending to a known user or broadcasting to all users)
    def send_message(self, request, _context):
        from_user = request.from_user
        to_user = request.to_user
        msg = request.message
        print("sending message from: " + from_user + " to: " + str(to_user))
        result = self.app.send_message(from_user, to_user, msg)

        # Write the new state to "database" and broadcast to child replicas
        self._handle_state_update()

        return chat.ChatReply(message = result)

    # list users matching with a wildcard
    def list_users(self, request, _context):
        wildcard = request.wildcard
        result = self.app.list_users(wildcard)

        if result:
            return chat.ChatReply(message = result)
        else:
            return chat.ChatReply(message= "No users to list.")

    # get messages for a user
    # if a user has been deleted by another account, they are alerted
    def get_message(self, request, _context):
        username = request.user        
        msg = self.app.get_messages(username)
        self.app.save_state()
        if msg == 100:
            return chat.ChatReply(message="LOGGED_OUT")
        else:
            return chat.ChatReply(message = msg)

    # delete user
    def delete_user(self, request, _context):
        user_to_delete = request.to_user
        user_deleting = request.from_user
        response = self.app.delete_user(user_to_delete, user_deleting)
        if response == True:
            print("User " + user_to_delete + " deleted by " + user_deleting)
            response = "Success."
        
        # Write the new state to "database" and broadcast to child replicas
        self._handle_state_update()

        return chat.ChatReply(message = response)

    # logout user
    def logout_user(self, request, _context):
        user = request.username
        response = self.app.logout_user(user)
        if response == True:
            print("Logging out user " + user)
            response = "SUCCESS"
        else: response = "Error logging out."

        # Write the new state to "database" and broadcast to child replicas
        self._handle_state_update()
        
        return chat.ChatReply(message = response)


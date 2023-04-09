from concurrent import futures

import grpc
import time
import threading
import logging

from app import App 
from config import config

import chat_pb2 as chat
import chat_pb2_grpc as rpc

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
    def __init__(self, address, port):
        self.address = address
        self.port = port

# define all of the grpc functions on the server side
class ChatServer(rpc.ChatServicer):

    def __init__(self, parent_replicas=[], is_primary=False):
        self.state = 0 # Test value, can ignore
        self.parent_replicas = parent_replicas
        self.server_id = len(parent_replicas) # 0, 1, 2
        self.is_primary = is_primary
        self.state_updates = []
        self.app = App(load_data=True)

        # Create a connection for each parent replica
        self.conns = {}
        for ind, replica in enumerate(self.parent_replicas):
            channel = grpc.insecure_channel(replica.address + ':' + str(replica.port))
            conn = rpc.ChatStub(channel)
            self.conns[ind] = conn
            threading.Thread(target=self.__listen_for_state_updates, args=(ind,), daemon=True).start()

            # Subscribe to channel connectivity. Maybe combine this with self.conns so failed channels are removed. Then we 
            # can use this to know when `self` is the primary.
            channel.subscribe(lambda event: self.__channel_connectivity_callback(event, ind))

    # TODO: This is never called when I exit the program on Terminal.
    def __channel_connectivity_callback(self, event, conn_ind):
        print("Callback called")
        # Remove the channel from self.conns
        if event == grpc.ChannelConnectivity.SHUTDOWN:
            print(f"Connection to server {conn_ind} ended.")
            del self.conns[conn_ind]

        # If no connections remain, set self to primary
        if not self.conns:
            self.is_primary = True

    def __listen_for_state_updates(self, conn_ind):
        """
        conn_ind (int): The index of the connection
        """
        try:
            for val in self.conns[conn_ind].StateUpdateStream(chat.Empty()):
                print(f"Server {self.server_id} received message: {val}")
                self.state = int(val.test)
                # users = pickle.loads(val.bytes)
                # self.app = App(users=users) 
        except Exception as e:
            print("Error occurred")
            print(e)
            del self.conns[conn_ind]

            # If no connections remain, set self to primary
            if not self.conns:
                self.is_primary = True
                print(f"Server {self.server_id} is now the primary.")

            return

    # The stream which will be used to send state updates to child_replica.
    def HeartbeatStream(self, request, context):
        """
        This is a response-stream type call. This means the server can keep sending messages
        Every client opens this connection and waits for server to send new messages
        :param request_iterator:
        :param context:
        :return:
        """
        # For every client an infinite loop starts (in gRPC's own managed thread)
        n = 0
        while True:
            # Only primary sends state updates
            if self.is_primary:
                n += 1                    
                yield chat.Heartbeat(timestamp=str(n))
            time.sleep(1)

    # TODO: Modify so that updates are removed from `self.state_updates` when they are yielded.
    def StateUpdateStream(self, request, context):
        while True:
            if self.is_primary:
                update = None
                yield update

    def StateUpdate(self):
        pass


    # create a user--> 3 cases: 
    # (1) user is new, create a new account 
    # (2) user is already logged in, refuse the login. 
    # (3) user is already registered but not logged in. They are re-logged in and able to join.
    def create_user(self, request, _context):
        username = request.username
        print("Joining user: " + username)
        result = self.app.create_user(username)
        if result == 0:
            response = "SUCCESS"
        elif result == 1:
            response = "This username is already logged in. Please choose another one."
        else:
            response = str("Welcome back " + username + " !")
        self.app.save_state()
        return chat.ChatReply(message=response)

    # send message (passes to App class, which will handle either 
    # sending to a known user or broadcasting to all users)
    def send_message(self, request, _context):
        from_user = request.from_user
        to_user = request.to_user
        msg = request.message
        print("sending message from: " + from_user + " to: " + str(to_user))
        result = self.app.send_message(from_user, to_user, msg)
        self.app.save_state()

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
        self.app.save_state()
        return chat.ChatReply(message = response)

    # logout user
    def logout_user(self, request, _context):
        user = request.username
        response = self.app.logout_user(user)
        if response == True:
            print("Logging out user " + user)
            response = "SUCCESS"
        else: response = "Error logging out."

        self.app.save_state()
        return chat.ChatReply(message = response)


    
if __name__ == '__main__':
    address = "0.0.0.0"
    replicas = [Replica(address, 5002), Replica(address, 5003), Replica(address, 5004)]
    # Simple loop to initialize ChatServer instances with the appropriate parent replicas
    parents = []
    servers = []
    for repl in replicas:
        # the workers is like the amount of threads that can be opened at the same time, when there are 10 clients connected
        # then no more clients able to connect to the server.
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # create a gRPC server
        is_primary = (len(parents) == 0) # Set the first to the primary
        rpc.add_ChatServiceServicer_to_server(ChatServer(parent_replicas=parents, is_primary=is_primary), server)  # register the server to gRPC
        # gRPC basically manages all the threading and server responding logic, which is perfect!
        print('Starting server. Listening...')
        server.add_insecure_port('[::]:' + str(repl.port))
        server.start()
        servers.append(server)
        parents.append(repl)

    # for ind, server in enumerate(servers):
    #     server.wait_for_termination()

    curr_ind = 0
    while curr_ind < 3:
        time.sleep(5)
        print(f"Stopping server {curr_ind}")
        servers[curr_ind].stop(grace=None)
        curr_ind += 1

    # # Server starts in background (in another thread) so keep waiting
    # # if we don't wait here the main thread will end, which will end all the child threads, and thus the threads
    # # from the server won't continue to work and stop the server
    # while True:
    #     time.sleep(64 * 64 * 100)
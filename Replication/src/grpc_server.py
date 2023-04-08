from concurrent import futures

import grpc
import chat_pb2
import chat_pb2_grpc
from app import App
import logging
import sys
from time import sleep
from threading import Thread
from config import config

chatServer = App()
leader = True

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


# define all of the grpc functions on the server side
class Chat(chat_pb2_grpc.ChatServicer):

    # create a user--> 3 cases: 
    # (1) user is new, create a new account 
    # (2) user is already logged in, refuse the login. 
    # (3) user is already registered but not logged in. They are re-logged in and able to join.
    def create_user(self, request, _context):
        username = request.username
        print("Joining user: " + username)
        result = chatServer.create_user(username)
        if result == 0:
            response = "SUCCESS"
        elif result == 1:
            response = "This username is already logged in. Please choose another one."
        else:
            response = str("Welcome back " + username + " !")
        return chat_pb2.ChatReply(message=response)

    # send message (passes to App class, which will handle either 
    # sending to a known user or broadcasting to all users)
    def send_message(self, request, _context):
        from_user = request.from_user
        to_user = request.to_user
        msg = request.message
        print("sending message from: " + from_user + " to: " + str(to_user))
        result = chatServer.send_message(from_user, to_user, msg)
        return chat_pb2.ChatReply(message = result)


    # list users matching with a wildcard
    def list_users(self, request, _context):
        wildcard = request.wildcard
        result = chatServer.list_users(wildcard)

        if result:
            return chat_pb2.ChatReply(message = result)
        else:
            return chat_pb2.ChatReply(message= "No users to list.")

    # get messages for a user
    # if a user has been deleted by another account, they are alerted
    def get_message(self, request, _context):
        username = request.user
        msg = chatServer.get_messages(username)
        if msg == 100:
            return chat_pb2.ChatReply(message="LOGGED_OUT")
        else:
            return chat_pb2.ChatReply(message = msg)

    # delete user
    def delete_user(self, request, _context):
        user_to_delete = request.to_user
        user_deleting = request.from_user
        response = chatServer.delete_user(user_to_delete, user_deleting)
        if response == True:
            print("User " + user_to_delete + " deleted by " + user_deleting)
            response = "Success."
        return chat_pb2.ChatReply(message = response)

    # logout user
    def logout_user(self, request, _context):
        user = request.username
        response = chatServer.logout_user(user)
        if response == True:
            print("Logging out user " + user)
            response = "SUCCESS"
        else: response = "Error logging out."
        return chat_pb2.ChatReply(message = response)
    
    def say_hello(self, request, _context):
        response = "hello there!"
        return chat_pb2.ChatReply(message = response)


class ServerThread(Thread):

    def __init__(self, port, replica):
        Thread.__init__(self)
        self.port = port
        self.replica = replica
        self.start()
    
    # kill the thread
    def kill(self):
        sys.exit()

    # main loop for the server thread, it constantly polls for messages from the server to the client
    def run(self):

        connectionString = str(SERVER_HOST + ":" + str(self.port))
        print("Connecting on: " + connectionString)

        # initialize grpc channel
        with grpc.insecure_channel(connectionString) as channel:
            stub1 = chat_pb2_grpc.ChatStub(channel)

            while True:
                try: 
                    # poll the replica constantly
                    response = stub1.say_hello(chat_pb2.ServerRequest(message = "hi!"))
                
                    print(response)
                    sleep(1)
                except:
                    print("Replica server at port {" + str(self.port) +"} has failed!")
                    self.kill()



def serve(order):
    # server is the leader
    if order == 1: 
        connectionString = str(SERVER_HOST + ":" + str(SERVER_PORT))
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
        chat_pb2_grpc.add_ChatServicer_to_server(Chat(), server)
        server.add_insecure_port(connectionString)
        server.start()
        print("GRPC Server started, listening on " + connectionString)
        t1 = ServerThread(REPLICA1_PORT, 2)
        t2 = ServerThread(REPLICA2_PORT, 3)
        server.wait_for_termination()
 
  # server is a replica     
    else:
        if order == 2:
            connectionString = str(SERVER_HOST + ":" + str(REPLICA1_PORT))
        else:
            connectionString = str(SERVER_HOST + ":" + str(REPLICA2_PORT))      
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
        chat_pb2_grpc.add_ChatServicer_to_server(Chat(), server)
        server.add_insecure_port(connectionString)
        server.start()
        print("GRPC Server started, listening on " + connectionString)
        server.wait_for_termination()




if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage Error: Please enter an integer 1, 2, or 3 to indicate where in the leadership order this server is. For example, the leader would be 'python3 grpc_server.py 1'.")
        
    elif  not(sys.argv[1] == "1" or sys.argv[1] == "2" or sys.argv[1] == "3"):
        print("Usage Error: Please enter an integer 1, 2, or 3 to indicate where in the leadership order this server is. For example, the leader would be 'python3 grpc_server.py 1'.")

    else: 
        order = int(sys.argv[1])
        serve(order)

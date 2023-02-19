from concurrent import futures

import grpc
import chat_pb2
import chat_pb2_grpc
from app import App
import logging
from config import config

chatServer = App()

# Logging config
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)


# Server config
SERVER_HOST = config["SERVER_HOST"]
SERVER_PORT = config["SERVER_PORT"]
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
        print("sending message from: " + from_user + " to: " + to_user)
        result = chatServer.send_message(from_user, to_user, msg)
        return chat_pb2.ChatReply(message = result)


    # list users matching with a wildcard
    def list_users(self, request, _context):
        wildcard = request.wildcard
        result = chatServer.list_users(wildcard)

        if result:
            return chat_pb2.ChatReply(message = result)
        else:
            return chat_pb2.ChatReply(message= "Could not list users.")

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


def serve():
    connectionString = str(SERVER_HOST + ":" + str(SERVER_PORT))
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    chat_pb2_grpc.add_ChatServicer_to_server(Chat(), server)
    server.add_insecure_port(connectionString)
    server.start()
    print("GRPC Server started, listening on " + connectionString)
    server.wait_for_termination()


if __name__ == '__main__':
    serve()

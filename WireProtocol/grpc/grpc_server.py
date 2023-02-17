from concurrent import futures

import grpc
import chat_pb2
import chat_pb2_grpc
from app import App

chatServer = App()


class Chat(chat_pb2_grpc.ChatServicer):

    def create_user(self, request, _context):
        username = request.username
        print("New user: " + username)
        result = chatServer.create_user(username)
        response = "success!" if result else "failed to create new user :("
        return chat_pb2.ChatReply(message=response)

    # send message from one logged in user to another
    def send_message(self, request, _context):
        return

# list users matching with a wildcard
    def list_users(self, request, _context):
        return

# read a message that has been sent to the logged in user
    def get_message(self, request, _context):
        return

# delete user
    def delete_user(self, request, _context):
       return



def serve():
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServicer_to_server(Chat(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
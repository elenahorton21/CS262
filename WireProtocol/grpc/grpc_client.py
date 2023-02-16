"""
Python program to implement client side of chat application.

TODO: How can the client know when the server has disconnected?
TODO: Refactor to make cleaner.
"""
import socket
import select
import sys
import chat_pb2
import chat_pb2_grpc
import grpc

"MAX_BUFFER_SIZE": 1024


def run():
    # Initialize TCP socket
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = chat_pb2_grpc.ChatStub(channel)
        response = None
        username = input("Enter your username:")
        response = stub.create_user(chat_pb2.UserRequest(username=username))
        print(f"Welcome to the chatroom {username}!")
            
 
            

if __name__ == "__main__":
    # parse and check arguments
    # TODO: Add defaults and better input handling
    # if len(sys.argv) != 4:
    #     print ("Correct usage: script, IP address, port number")
    #     exit()
    # IP_address = str(sys.argv[1])
    # port = int(sys.argv[2])
    # IP_address = "127.0.0.1"
    # port = 50015 # server's port

    run()
"""
Python program to implement client side of chat application.
"""
import sys
import chat_pb2
import chat_pb2_grpc
import grpc
from threading import Thread
from time import sleep

MAX_BUFFER_SIZE = 1024

def handle_input(input, username, stub):
    try: 
        if input.startswith("/list"):
            if len(input.split(" ")) == 1:
                wildcard = None
            else:
                wildcard1 = input.split(" ")[1]
                wildcard = wildcard1.replace('\n', "")
            response = stub.list_users(chat_pb2.ListRequest(wildcard=wildcard))
            print(response)
            return
        
        # DELETE user case
        elif input.startswith("/delete"):
            input = input.strip()
            user_to_delete1 = input.split(" ")[1]
            user_to_delete = user_to_delete1.replace('\n',"")
            response = stub.delete_user(chat_pb2.DeleteRequest(from_user = username, to_user = user_to_delete))
            print(str(response))
            return

        # user requesting to send a direct message to a specified recipient
        elif input.startswith(">>"):
            msgList = input.split(":")
            usernameToSend1 = msgList[0].replace(">", "")
            usernameToSend = usernameToSend1.replace(" ", "")
            msgText = msgList[1]
            return stub.send_message(chat_pb2.MessageRequest(from_user=username, to_user=usernameToSend, message=msgText))

        # user logging in as a different user
        elif input.startswith("/login"):
            input = input.strip()
            username1 = input.split(" ")[1]
            username = username1.replace('\n',"")
            response = login(stub, username)
            print(str(response))
            return
    
        # broadcast message to all
        else: 
            return stub.send_message(chat_pb2.MessageRequest(from_user=username, to_user=None, message=input))
        
    except Exception:
        print("Improper usage.")
        print("(1) Send a message to all --> type message and press enter")
        print("(2) Send a message to specified recipient --> '>> [recipient]: [message]'")
        print("(3) List all recipients w/ optional wildcard --> '/list [wildcard]'")
        print("(4) Delete a specified recipient account --> '/delete [recipient]'")
        print("(5) Login as different user --> '/login [username]'")


def login(stub, username):
    response = stub.create_user(chat_pb2.UserRequest(username=username))
    return response



def getServerMessagesThread(stub, username):
    while True:
        # check constantly if we have inbound messages
        response = stub.get_message(
            chat_pb2.GetRequest(user = username))
        if response.message == "LOGGED_OUT":
            print("You have been deleted from the chat. Please login again.")
        elif response.message != "NONE":
            print(response.message)
        sleep(.5)

def startServerThread(chatStub, username):
    t = Thread(target=getServerMessagesThread, args=(chatStub, username))
    t.start()
    return

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = chat_pb2_grpc.ChatStub(channel)
        username = input("Enter your username:")
        response = login(stub, username)
        print(response)
        startServerThread(stub, username)

        # Display initial usage suggestions
        print("")
        print("USAGE:")
        print("(1) Send a message to all --> type message and press enter")
        print("(2) Send a message to specified recipient --> '>> [recipient]: [message]'")
        print("(3) List all recipients w/ optional wildcard --> '/list [wildcard]'")
        print("(4) Delete a specified recipient account --> '/delete [recipient]'")
        print("(5) Login as different user --> '/login [username]'")


        while True:
            newInput = sys.stdin.readline()
            handle_input(newInput, username, stub)
            

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

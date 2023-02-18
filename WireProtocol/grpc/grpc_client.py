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
            return True
        
        # delete user case
        elif input.startswith("/delete"):
            input = input.strip()
            user_to_delete1 = input.split(" ")[1]
            user_to_delete = user_to_delete1.replace('\n',"")
            response = stub.delete_user(chat_pb2.DeleteRequest(from_user = username, to_user = user_to_delete))
            print(str(response))
            return True

        # user requesting to send a direct message to a specified recipient
        elif input.startswith(">>"):
            msgList = input.split(":")
            usernameToSend1 = msgList[0].replace(">", "")
            usernameToSend = usernameToSend1.replace(" ", "")
            msgText = msgList[1]
            response = stub.send_message(chat_pb2.MessageRequest(from_user=username, to_user=usernameToSend, message=msgText))
            return True

        # user logging in as a different user
        elif input.startswith("/logout"):
            input = input.strip()
            response = logout(stub, username)
            print(str(response))
            if response.message == "SUCCESS":
                print("You have successfully logged out.")
                return False
            return True
    
        # broadcast message to all
        else: 
            response = stub.send_message(chat_pb2.MessageRequest(from_user=username, to_user=None, message=input))
            return True
        
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

def loginUser(response):
    if response.message == "This username is already logged in. Please choose another one.":
        return False
    else:
        return True

def logout(stub, username):
    response = stub.logout_user(chat_pb2.UserRequest(username= username))
    return response
    
    



# this thread handles the constant get message requests from the client. 
# To be honest, this doesn't seem like the best bi-directional solution, but it is working within
# the confines of gRPC. Future questions would be how to handle client connection state on the
# server as opposed to the client.

# ServerThread--> takes the gRPC stub channel to send requests on, the client username, and the state
# of whether or not the client is logged in. 

class ServerThread(Thread):

    def __init__(self, stub, username):
        Thread.__init__(self)
        self.stub = stub
        self.username = username
        self.logged_in = False
        self.start()
    
    def kill(self):
        sys.exit()


    def run(self):
        while True:
            try: 
                # check constantly if we have inbound messages
                response = self.stub.get_message(
                    chat_pb2.GetRequest(user = self.username))

                # handle the case of having our account deleted-> exit gracefully
                if response.message == "LOGGED_OUT":
                    print("You have been deleted from the chat. Press Enter to ESC")
                    self.logged_in = False
                    self.kill() # exit the thread because the user has been deleted
                
                # display new messages, do nothing if there are no new messages
                elif response.message != "NONE":
                    print(response.message)
                sleep(.5)
            except:
                print("Bye!")
                self.kill()

def run():
    logged_in = False
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = chat_pb2_grpc.ChatStub(channel)

        while not logged_in:
            username = input("Enter your username:")
            response = login(stub, username)
            print(response)
            logged_in = loginUser(response)

        t = ServerThread(stub, username)
        t.logged_in = True
            
        
        # Display initial usage suggestions
        print("")
        print("USAGE:")
        print("(1) Send a message to all --> type message and press enter")
        print("(2) Send a message to specified recipient --> '>> [recipient]: [message]'")
        print("(3) List all recipients w/ optional wildcard --> '/list [wildcard]'")
        print("(4) Delete a specified recipient account --> '/delete [recipient]'")
        print("(5) Logout --> '/logout'")


        while t.logged_in == True and logged_in == True:
            newInput = sys.stdin.readline()
            logged_in = handle_input(newInput, username, stub)
        
        channel.close()
        sys.exit()
            

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

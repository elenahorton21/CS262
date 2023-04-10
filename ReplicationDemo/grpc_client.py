"""
Python program to implement client side of chat application.
"""
import sys
import chat_pb2
import chat_pb2_grpc
import grpc
from threading import Thread
from time import sleep
from config import config


# Configuration
MAX_BUFFER_SIZE = config["MAX_BUFFER_SIZE"]
SERVER_ADDRESS = config["SERVER_ADDRESS"]
SERVER_PORT = config["SERVER_PORT"]
REPLICA1_PORT = config["REPLICA1_PORT"]
REPLICA2_PORT = config["REPLICA2_PORT"]
MAX_USERNAME = 20


# main function for handling the user input and translating it into messages or commands
def handle_input(input, username, stub):
    try: 

        # list users
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
            response = stub.send_message(chat_pb2.ServerRequest(from_user=username, to_user=usernameToSend, message=msgText))
            return True

        # user logging out
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

    # improper user input, remind the user of the usage    
    except Exception:
        print("Improper usage.")
        print("(1) Send a message to all --> type message and press enter")
        print("(2) Send a message to specified recipient --> '>> [recipient]: [message]'")
        print("(3) List all recipients w/ optional wildcard --> '/list [wildcard]'")
        print("(4) Delete a specified recipient account --> '/delete [recipient]'")
        print("(5) Logout --> '/logout'")


# helper functions to login the user
def login(stub, username):
    if len(username) > MAX_USERNAME:
        print (f"This username is too long. Please enter a username < {MAX_USERNAME} characters")
        return False
    response = stub.create_user(chat_pb2.UserRequest(username=username))
    return response

# check if the user is already logged in, otherwise login is successful
def loginUser(response):
    if response.message == "This username is already logged in. Please choose another one.":
        return False
    else:
        return True

# logout the user
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
    
    # kill the thread
    def kill(self):
        sys.exit()

    # main loop for the server thread, it constantly polls for messages from the server to the client
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
                self.kill()

# main loop for the client
def run(IPaddress, port, info):
    logged_in = info[0]
    username = info[1]
    connectionString = str(IPaddress + ":" + str(port))
    print("Connecting on: " + connectionString)

    # initialize grpc channel
    with grpc.insecure_channel(connectionString) as channel:
        stub = chat_pb2_grpc.ChatStub(channel)

        # first check for a conenection
        try: response = stub.check_connection(chat_pb2.Empty())
        except: 
            print("Channel " + connectionString + " is closed.")
            return [False, None]

        # run the login loop until the user successfully logs in
        while not logged_in:
            username = input("Enter your username:")
            response = login(stub, username)
            print(response)
            if response:
                logged_in = loginUser(response)

        # once logged in, start the server thread to get messages from the server
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

        # as long as the user is logged in, read their input
        while t.logged_in == True and logged_in == True:
            newInput = sys.stdin.readline()

            # ensure that the input is less than the max length
            if len(newInput) > MAX_BUFFER_SIZE:
                print("ERROR: Message too long.")
            else: 
                logged_in = handle_input(newInput, username, stub) # only returns false if the user is no longer logged in
        
        channel.close()
        
        # see if the leader failed or if the user logged out
        if logged_in == False:
            sys.exit()
        else:
            return [True, username]


if __name__ == "__main__":
    IP_address = SERVER_ADDRESS
    port = SERVER_PORT

    # main connection logic --> start with the leader, then if it fails, rejoin to a replica. If the replica is down, it will try the other one.
    try: info = run(IP_address, port, [False, None])
    except: print("Primary server is down.")
    try: info1 = run(IP_address, REPLICA1_PORT, info)
    except: print("First replica is down.")
    try: info2 = run(IP_address, REPLICA2_PORT, info1)
    except: print("All servers are currently down.")


# Overview
This folder contains the socket implementation of our chat app.

# Usage
To run this application, first start the server by running `python3 -m server.py`.

Then, in another terminal window, start the client by running `python3 -m client.py`

To configure the host and port you are running on, you must edit the `config.py` file in this `src` folder. 

## Client usage

Client users can take several potential actions:

#### Login 
This will be prompted before any other options are available. You must enter a username. If the username is currently being used, or the inputted username is invalid (i.e. contains non-alphanumeric characters or exceeds the maximum username length), it will be refused. Otherwise, if the username was previously registered, you will be logged in and can input `/queue` to receive your queued messages. If it is a new unique username, an account will be created and you can begin using the app.

#### Send a message

Private messages must be specified by the user with `>> username: [message]`. If `>> username:` is not specified, then whatever text is entered will be broadcast to all active users. It is very important to indicate that you are sending to a specific recipient by clarifying `>>` followed by the desired recipient `username`. If `username` does not exist, or `[message]` exceeds the limit of 280 characters, the console will display an error message.  

#### List accounts

Users must enter `/list` to list all accounts or `/list [wildcard]` to list a subset of accounts by a wildcard. The wildcard is formatted as a regular expression (i.e. the wildcard `e` will return all names that begin with e, the wildcard `.a` will return all names that have `a` as the 2nd character, the wildcard `.*i` will return all names that have an `i` anywhere in them, etc.). If there are more than 30 usernames that satisfy the wildcard (or 30 accounts in the case that a wildcard is not specified), only 30 usernames will be returned and the console will display a message explaining this.

#### Delete an account

Users must enter `/delete [account]` to delete an account. They can delete any account that is not active. If `[account]` is not a registered account or is active, an error message will be displayed.

#### Logout

To successfully exit the chat, users must log out by entering `/logout`. This will gracefully exit the chat and preserve the username so you can log back in later. 


#### Getting messages

To receive messages that were sent directly to you (i.e. via `>>[your_username]: [message]`) while you were not logged in, you can enter `/queue`.

# Structure

This code has three main components, along with supplemental files:
1) `grpc_client.py`: This is the client module. It contains the gRPC stubs to invoke remote calls on the `grpc_server.py` module. All of the logic for running and handling user input is contained in this module.
2) `grpc_server.py`: This is the server module. It contains all of functions that can be remotely called by the client. To handle the overall state and memory of the application, it passes calls to `app.py`.
3) `app.py`: This is the app state class that our chat application uses to keep track of users and messages. The `grpc_server.py` instantiates an `App` object and, through calls from its clients, manipulates the object throughout its lifetime to keep track of new users, removed users, and messages associated with all users. 
4) Supplemental files include `chat.proto`, our prototype definition file, `build_proto_file.sh`, a simple script to auto-generatre the associated grpc files `chat_pb2.py`, `chat_pb2_grpc.py`, and `chat_pb2.pyi`. `config.py` contains the pre-defined settings for maximum connections, max buffer length, hostname, port, and server IP address.

# Testing
You can run `pytest -v grpc_unit_test.py` to view the output of the unit tests on different aspects of the solution. 

# Limitations

1) The primary limitation of this code is that users must logout to be able to log back in again later. This could be solved in the future with some way for the grpc server to be alerted if a client is no longer requesting messages (calling the `get_messages` function on the server). 
2) Another limitation is that only messages shorter than the defined `MAX_BUFFER_LENGTH` can be sent in our application. This is consistent with the specs clarified in Ed postings. 

# Differences from non-gRPC Implementation

1) The primary difference is that the grpc implementation is handing states on the client side rather than the server side. Since there was no clear way to keep track of client connections, the client has a thread, in our case, the `ServerThread` class, that constantly polls the server for new messages. As a result, the client has to keep track of whether or not it is logged in and communicate that to the server, which also creates our greatest limitation of not being able to successfully logout if the client does not explicitly do so. 

2) Due to the simplified design of gRPC, this also means that the structure of our modules look different between the non-GRPC and GRPC implementations. Because the client can just call remotely to the server, we structure our gRPC server to simply execute these calls, making function calls directly to the `App` object that holds our application's state. In the non-gRPC implementation, several function calls are used to properly create the message protocol and safely access the application resources by passing the client connection details between modules. However, in the gRPC case, the application is tracking client connecetions for us, so none of that code is necessary. Consequently, our gRPC app has a simpler design. 

3) Performance and buffer sizes--> in our application, there is not an obvious difference other than slower delivery of messages to the client in the gRPC case because of the client's `ServerThread` polling for new messages. This is a design choice, and less reflective of the actual latency of gRPC vs. sockets. For a chat application with limited large data transfer, the use of pure sockets still appears faster --> communication is instantaneous without the need for app layer translations in gRPC. However, if this application were to grow to handling larger data streams, gRPC would be a much more efficient way of packaging this information. 

# Engineering Notebook

Some big decisions that were made:

1) How to handle client state. In the non-gRPC example, we could constantly ping the sockets and see if any clients were disconnected, thus keeping track of their log in status. However, in the gRPC implementation, we couldn't see a good way to do this (there very well may be one though). As a result, the client itself is keeping track of it's logged in state, and thus the app prevents the client from taking any action before being logged in, and it also automatically exits the application if the client is logged out to prevent hung states. This was accomplished by the following decision:
    - creating a `ServerThread` class to contantly poll the server using the `GetMessage` function. If it gets a message indicating that the client has been logged out, it returns this and the thread exits after alerting the client that they have been logged out. The thread keeps track of this by having an internal state `self.logged_in`.
    - creating a `logged_in` boolean value within the client that keeps track of whether or not the client is logged in. The client only can perform actions as usual if both the recieving `ServerThread` and the client itself have these values as `True`. Otherwise, the client is logged out and the application will gracefully exit. 

2) Redesigning the server code to be simplified for the gRPC scenario. Once we started working on the gRPC scenario, it became clear that our existing code was overly complex for what we needed in the gRPC world. Because gRPC is able to keep track of client connections for us, we didn't need to be passing client connection information between the server module and App object, and the App object didn't need a field for client connections. We changed the structure to just keep track of client usernames and their associated messages, and it is now the client's responsibility to ask for those messages to be delivered (in our solution, the client is doing this continuously). There are more implications of this and decisions made along the way:
    - Simplify the client to just handle user input and make direct calls to the server. This simplified the logic to most of it being handled in the `handle_user_input` function. 
    - Simplify the `App` class to only include users and their messages. We added a `.logged_in` field to the `User` class as a way to explicitly track if the user is logged in or not based on calls from the client (i.e. `register` and `logout`). This is what prevents a user from logging in on multiple sessions at once. 
    - The `grpc_server.py` module now is just one function for each explicit user action all held within the `Chat` class. All of the logic for handling each use case is in there, and the only other function is the main `run` loop which instantiates the gRPC connection and starts the server. 
# Overview
This folder contains the grpc implementation of our chat app. There are several differences from our non-gRPC implementation, which we will explain throughout this document.

# Usage
To run this application, first start the server by running `python3 grpc_server.py`.

Then, in another terminal window, start the client by running `python3 grpc_client.py`

To configure the host and port you are running on, you must edit the `config.py` file in this `grpc` folder. 

## Client usage

Client users can take several potential actions:

#### Login 
This will be prompted before any other options are available. You must enter a username. If the usernamae is already actively in use, it will be refused. If it is a known username but you are returning, you will be logged in and have any missing messages delivered to you. And if it is a new unique username, an account will be created and you can begin using the app.

#### Send a message

Private messages must be specified by the user with `>> username: [message]`. If `>> username:` is not specified, then whatever text is entered will be broadcast to all users. It is very important to indicate that you are sending to a specific recipient by clarifying `>>` followed by the desired recipient `username`. 

#### List accounts

Users must enter `/list` to list all accounts or `/list [wildcard]` to list a subset of accounts by a wildcard. 

#### Delete an account

Users must enter `/delete [account]` to delete an account. They can delete their own account or any other known account (no security considerations). 

#### Logout

To successfully exit the chat, users must log out by entering `/logout`. This will gracefully exit the chat and preserve the username so you can log back in later. 

**LIMITATION**: In the gRPC implementation, if a client exits unexpectedly without logging out, then that username will be stale when the return later. The solution is to have another user delete their account, thus allowing the user to log in as if creating a new account.

#### Getting messages

There are no commands to explicitly recieve messages, they will come in as they are sent by other users. If you are re-logging in and have missed messages, they will be delivered to you upon your login. 

# Structure

This code has three main components, along with supplemental files:
1) `grpc_client.py`: This is the client module. It contains the gRPC stubs to invoke remote calls on the `grpc_server.py` module. All of the logic for running and handling user input is contained in this module.
2) `grpc_server.py`: This is the server module. It contains all of functions that can be remotely called by the client. To handle the overall state and memory of the application, it passes calls to `app.py`.
3) `app.py`: This is the app state class that our chat application uses to keep track of users and messages. The `grpc_server.py` instantiates an `App` object and, through calls from its clients, manipulates the object throughout its lifetime to keep track of new users, removed users, and messages associated with all users. 
4) Supplemental files include `chat.proto`, our prototype definition file, `build_proto_file.sh`, a simple script to auto-generatre the associated grpc files `chat_pb2.py`, `chat_pb2_grpc.py`, and `chat_pb2.pyi`. `config.py` contains the pre-defined settings for maximum connections, max buffer length, hostname, port, and server IP address.  

# Limitations

1) The primary limitation of this code is that users must logout to be able to log back in again later. This could be solved in the future with some way for the grpc server to be alerted if a client is no longer requesting messages (calling the `get_messages` function on the server). 
2) Another limitation is that only messages shorter than the defined `MAX_BUFFER_LENGTH` can be sent in our application. This is consistent with the specs clarified in Ed postings. 

# Differences from non-gRPC Implementation

1) Handing states on the client side rather than the server side

2) Differences in behavior --> logging out

# Engineering Notebook

Some big decisions that were made:

1) How to handle client state. In the non-gRPC example, we could constantly ping the sockets and see if any clients were disconnected, thus keeping track of their log in status. However, in the gRPC implementation, we couldn't see a good way to do this (there very well may be one though). As a result, the client itself is keeping track of it's logged in state, and thus the app prevents the client from taking any action before being logged in, and it also automatically exits the application if the client is logged out to prevent hung states. This was accomplished by the following decision:
    - creating a `ServerThread` class to contantly poll the server using the `GetMessage` function. If it gets a message indicating that the client has been logged out, it returns this and the thread exits after alerting the client that they have been logged out. The thread keeps track of this by having an internal state `self.logged_in`.
    - creating a `logged_in` boolean value within the client that keeps track of whether or not the client is logged in. The client only can perform actions as usual if both the recieving `ServerThread` and the client itself have these values as `True`. Otherwise, the client is logged out and the application will gracefully exit. 

2) Redesigning the server code to be simplified for the gRPC scenario.

3) Simplifying the app code for the gRPC scenario--> no need to keep track of conenections.

# Future Work
3) Unit tests
5) Write an engineering notebook/fill out the contents of this readme
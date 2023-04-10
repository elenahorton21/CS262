# CS 262 Design Exercise #3: Replication

# Overview
This folder contains our redesigned, 2-fault tolerant, persistent grpc chat application. This document will discuss the design principles, structure, and usage for the application. 

# Installation

To set up your environment to run our code:
1) Run `pip install -r requirements.txt` from this folder. 
2) Edit the `config.py` file to add your desired IP address and port numbers
3) Follow the usage instructions in the rest of this README to run the application

# Usage
To run this application, first start the lead server by running `python3 server_demo.py 0`.

Then, in other terminal windows (or devices) start the replica servers by running `python3 server_demo.py 1` and `python3 server_demo.py 2` respectively.

Then, in another terminal window (or a different device), start the client by running `python3 grpc_client.py`

To configure the host and port you are running on, you must edit the `config.py` file in this folder. 

## Client usage

Client users can take several potential actions:

#### Login 
This will be prompted before any other options are available. You must enter a username. If the usernamae is already actively in use, it will be refused. If it is a known username but you are returning, you will be logged in and have any missing messages delivered to you. And if it is a new unique username, an account will be created and you can begin using the app.

#### Send a message

Private messages must be specified by the user with `>> username: [message]`. If `>> username:` is not specified, then whatever text is entered will be broadcast to all users. It is very important to indicate that you are sending to a specific recipient by clarifying `>>` followed by the desired recipient `username`. 

#### List accounts

Users must enter `/list` to list all accounts or `/list [wildcard]` to list a subset of accounts by a wildcard. The wildcard is formatted as a regular expression (i.e. the wildcard `e` will return all names that begin with e, the wildcard `.a` will return all names that have `a` as the 2nd character, the wildcard `.*i` will return all names that have an `i` anywhere in them, etc.)

#### Delete an account

Users must enter `/delete [account]` to delete an account. They can delete their own account or any other known account (no security considerations). 

#### Logout

To successfully exit the chat, users must log out by entering `/logout`. This will gracefully exit the chat and preserve the username so you can log back in later. 

**LIMITATION**: In the gRPC implementation, a client can log in on multiple sessions at once with the same username. It does not adversely affect the funcionality of the chat application in other ways.

#### Getting messages

There are no commands to explicitly recieve messages, they will come in as they are sent by other users. If you are re-logging in and have missed messages, they will be delivered to you upon your login. 

# Structure

This code has a few key files, along with supplemental files:
1) `grpc_client.py`: This is the client module. It contains the gRPC stubs to invoke remote calls on the `grpc_server.py` module. All of the logic for running and handling user input is contained in this module.
2) `server_demo.py`: This is the primary server module. It creates an instance of the `server.py` module to handle communications between the clients and also between the other servers (all through grpc connections). To handle the overall state and memory of the application, it passes calls to `app.py`.
3) `app.py`: This is the app state class that our chat application uses to keep track of users and messages. The `server.py` instantiates an `App` object and, through calls from its clients, manipulates the object throughout its lifetime to keep track of new users, removed users, and messages associated with all users. 
4) The `app.pickle` file is the persistent data store of this chat application. Upon starting a new session, the `server` object will try to instantiate and `App` object from the `app.pickle` file. If the file does not exist, it will create a new one to save its state to throughout the chat's lifecycle. 
5) Supplemental files include `chat.proto`, our prototype definition file, `generate-proto.sh`, a simple script to auto-generatre the associated grpc files `chat_pb2.py`, `chat_pb2_grpc.py`, and `chat_pb2.pyi`. `config.py` contains the pre-defined settings for maximum connections, max buffer length, hostname, port, and server IP address.

# Testing
You can run `pytest` or `python3 -m pytest` from any folder to view the output of the unit tests on different aspects of the solution. 

We also ran several manual tests to evaluate proper fault tolerance behavior. These manual tests included:
1) Set up the system with 3 clients, then killing the lead server process. Check all client chat functionality. Then kill another replica and check all functionality again.
2) Set up the system with 1 client. Kill the lead server. Have another client join. Kill a replica. Have another client join. Check all chat functionality at each step.
3) Set up he system with 3 clients. Kill the 1st replica. Continue chat functionality. Kill the lead server. Ensure that all chat functionality continues through the 2nd replica. 
4) Set up the system with 3 clients. Send messages. Kill a client process. Send more messages. Kill the lead server. Log the client back in and see that all messages are still delivered. 

# Limitations

1) One limitation is that only messages shorter than the defined `MAX_BUFFER_LENGTH` can be sent in our application. This is consistent with the specs clarified in Ed postings. 
2) Another limitation is that the same username can be used across multiple sessions. This doesn't seem to negatively affect chat functionality, and is more of a design choice that could be improved in the future with a more robust client <--> stream that automatically logs the user out if a client crashes. 


# Distributed System Design

## Fault tolerance
We designed our system in the following graphical way: 

![Our distributed system design](./img/design.jpg)

We establish a connection order for clients to follow. First, they try to connect to the lead server. Then, if that fails, they try to connect to the first replica. Finally, if both the lead server and the replica are down, they try to connect to the second replica.

The replicas each are tracking the heartbeat(s) of the servers ahead of them in order. That is, the first replica is tracking the lead server's heartbeat, and the second replica is tracking the first replica and the lead server's heartbeat. If a server fails, they both know where they stand in the order and the highest-ordered active server takes over as the lead server. Simultaneously, the clients switch to the next active server in order, ensuring it is the true lead server.

## Persistence

Persistence is handled by a file, `app.pickle`, that each server reads from upon starting up. Whenever a change is initiated in the app state, the lead server broadcasts the change to the replicas and saves the app state to the `app.pickle` file. 


# Engineering Notebook

**4/1**: Designing our system. Debating having a lead server, or having the clients all broadcast to all replicas always. Did decide to use our grpc implementation because the thread management is all handled under the hood of grpc and it is much easier to define our calls (both for the application and for communication between the servers.)

**4/2**: Decided on a system where clients talk to a lead server. However, we are debating how to trigger a switch from lead server to the replicas. Came up with the idea to formally order the replicas, so if clients recognize that the server is down, they just switch to the next one in order. The downside of this is that it seems less elegant than the server's self-appointing a leader. 

**4/3**: Designed the initial system with a lead server and clients able to auto-switch to replicas when they crash. However, it's not a very good solution for the clients to trigger the switch because the replica server thread that is listening for connections can't access a state variable for the server to know it is now the leader. Doing a redesign on the server system.

**4/5**: Server system is resolved by introducing grpc streams to our proto file. These streams allow each of the servers to have a heartbeat with each other, allowing them to recognize themselves when a server goes down and switch into the leader role if necessary. Clients still automatically switch themselves. Added `HeartbeatStream` to the grpc proto file.

**4/6**: Working on state updates, added `StateUpdateStream` to teh grpc proto file. State updates are sent from each action module of the `server` module as bytes to the other servers. The servers then uses `pickle` to translate those bytes into our app data structure, and resets the app state to that value. We decided on this state update mechanism as opposed to smaller, specific state updates because it was a simpler solution and guaranteed that the state update stayed consistent. With this decision, we are sacrificing bandwidth for greater reliability.

**4/8**: Testing different scenarios manually, documenting each of these in our `Testing` section above. 

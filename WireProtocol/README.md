# CS 262: Wire Protocols Assignment

## Structure of this project
This project is organized into 3 main subfolders, `src`, `grpc`, and `tests`. 
    - `src` contains the code for the non-gRPC implementation of this chat application. To run this code, first `cd src` then run `python3 server.py` to start the server and `python3 client.py` to run the client. Any configuration of port, server address, or hostname should be done by editing the `config.py` file in the `src` folder.
    - `grpc` contains the code for the gRPC implementation of this chat application. To run this code, first `cd grpc` then run `python3 grpc_server.py` to start the server and `python3 grpc_client.py` to run the client. Similiarly to above, any configuration of port, server address, or hostname should be done by editing the `config.py` file in the `grpc` folder.
    - `tests` contain the code for testing our application.  

### Protocol Definition

We implement a pretty simple protocol to fulfill the defined functionality for this assignment. The primary structure is to have an initial keyword that defines the type of message, `TYPE|` followed by the specified username if applicable. 

#### Remove an account

`DELETE|username_to_delete`

#### List all accounts

`LIST|wildcard`

Note: if a wildcard is not provided, this will then list all accounts. Otherwise the server processes the wildcard and only lists the applicable accounts.

#### Register a new user

`USERNAME|username`

Note: the protocol requires that the client first registers their username upon connection. The server either recognizes this as a new username or identifies it as a previous account. 

#### Send a message

`MESSAGE|usernameFrom|usernameTo|[message]`

Note: if a `usernameTo` is not specified, then the message is broadcast to all users. The server interprets this by the client auto filling the `usernameTo` field as `TO_ALL`. 


### Client Usage

#### Send a message

Private messages must be specified by the user with `>> username: [message]`. If `>> username:` is not specified, then whatever text is entered will be broadcast to all users. It is very important to indicate that you are sending to a specific recipient by clarifying `>>` followed by the desired recipient `username`. 

#### List accounts

Users must enter `list` to list all accounts or `list: [wildcard]` to list a subset of accounts by a wildcard. 

#### Delete an account

Users must enter `delete [account]` to delete an account. They can delete their own account or any other known account (no security considerations). 


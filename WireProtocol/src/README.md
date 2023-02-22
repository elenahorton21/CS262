# Overview
This folder contains the socket implementation of our chat app.

# Usage
To run this application, first start the server by running `python3 -m src.server` from the `WireProtocol` directory.

Then, in another terminal window, start the client by running `python3 -m src.client` from the `WireProtocol` directory.

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

1) `protocol.py`: This module defines how messages between the client and server should be encoded and decoded. It defines a base `Message` class that is inherited by service-specific subclasses, e.g. `RegisterMessage`. The subclasses enforce that messages for a specific service have the required data fields. It also contains helper functions `decode_server_buffer` and `decode_client_buffer` that take a byte string as input and return a list of Message instances.
2) `client.py`: This is the client module. It contains the code for establishing and listening to the server socket, and sending and reading messages. It uses the classes and functions defined in `protocol.py` to encode user input and decode the byte strings received from the socket. 
3) `server.py`: This is the server module. It contains the code for initializing the server socket and creating a thread for handling each accepted client connection. It also contains a function for each service that takes a corresponding message and returns an appropriate response. To handle the overall state and memory of the application, it passes calls to `app.py`.
4) `app.py`: This is the app state class that our chat application uses to keep track of users and messages. Running `server.py` instantiates an `AppState` object and, through calls from its clients, manipulates the object throughout its lifetime to keep track of new users, removed users, and messages associated with all users. 
5) `config.py` contains the pre-defined settings for maximum connections, max buffer length, hostname, port, and server IP address.

# Testing
You can run `pytest` to run all unit tests. Before doing so, please install the dependencies with `pip install -r requirements.txt`.

# Limitations

1) Our implementation does not address potential race conditions arising from multiple client threads manipulating the same data in the `AppState` instance. However, our implementation is written so that `server.py` does not access or modify any data in `AppState` directly, so this could be relatively easily implemented by adding locks to the appropriate getter and setter functions in `app.py`.
2) Another limitation is that we do not handle cases where the user input contains our separator or end-of-message tokens. In these cases, the decoding may not work properly.

# Engineering Notebook

Some big decisions that were made:

1) We decided to define all app logic (adding users, queuing messages, etc.) in the `AppState` class, and have `server.py` only interact with it through getter and setter methods. While this meant that we needed to write more methods and unit tests, we felt it would be beneficial for several reasons. For one, it makes it easier to address race conditions that arise from separate threads manipulating the same data, since we can just add locks (i.e. `Lock()`) to the appropriate `AppState` functions. Secondly, we could easily persist data between sessions by creating an initializer for `AppState` that reads from some stored file. Lastly, it makes unit testing a bit more conveninent, since we can inject a mock `AppState` as a dependency to the functions in `server.py`, and patch the functions of `AppState`.

2) Following an explicit request-response format with client-server communication. We decided that each service (`list`, `delete`, etc.) should have a specific `Message` and `Response` subclass, and that client messages should be handled through functions that assume specific types, e.g. `handle_register(RegisterMessage) -> RegisterResponse`. With this design, we decouple the encoding and decoding of the socket buffers from the service logic, so for example `handle_regiser` can assume that the message contains a `username` field, and `client.py` can assume that the message it recieves has a `success` and `error` field. 

3) We added an end-of-message token and created helper functions `decode_server_buffer` and `decode_client_buffer` that take a byte string as input and return a list of `Message` instances. While in most cases our request-response format means that the client can expect to receive one message at a time, this is not always the intended result (e.g. with the message queue service, multiple messages can be sent at once), and it's possible that this can happen in unexpected cases as well. This functionality was designed to anticipate these cases.



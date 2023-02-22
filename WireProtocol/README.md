# CS 262: Wire Protocols Assignment

## Structure of this project
This project is organized into 3 main subfolders, `src`, `grpc`, and `tests`. `src` and `grpc` each contain more detailed REAMDEs of the implementation of each of our chat applications. `src` describes the chat application using our own protocol, and `grpc` describes our application using gRPC. More specifically: 

- `src` contains the code for the non-gRPC implementation of this chat application. To run this code, first `cd src` then run `python3 -m server.py` to start the server and `python3 -m client.py` to run the client. Any configuration of port, server address, or hostname should be done by editing the `config.py` file in the `src` folder.

 - `grpc` contains the code for the gRPC implementation of this chat application. To run this code, first `cd grpc` then run `python3 grpc_server.py` to start the server and `python3 grpc_client.py` to run the client. Similiarly to above, any configuration of port, server address, or hostname should be done by editing the `config.py` file in the `grpc` folder. To test this code, view the testing instructions described in the `grpc` folder's README file. 

 - `tests` contain the code for testing our application. The tests can be run with `pytest`. The tests depend on some
libraries that can be installed by calling `pip install -r requirements.txt` from the root directory.

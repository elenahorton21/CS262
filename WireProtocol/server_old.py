"""
Defines server behavior for chat application.
"""
import socket
import select
import argparse
import sys
from threading import Thread, Lock
import logging 

from app import AppState


# Logging config
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


# checks arguments
if len(sys.argv) != 3:
    print ("Correct usage: script, IP address, port number")
    exit()
 
# parse arguments 
IP_address = str(sys.argv[1])
Port = int(sys.argv[2])


server.bind((IP_address, Port))
server.listen(100)
 


 # Maintain knowledge of all clients
client_sockets = set()
known_users = dict()


def client_thread(client_socket):
    client_socket.send("Welcome to this chatroom!")
 
    # main message handling loop for each client/server thread
    while True:
        try:
            # Listen for a message from client socket
            message = client_socket.recv(2048) # TODO: Change to variable
            if message:
                handleMessage(message, conn, addr)
            else:
                remove(conn)
        except:
            continue


def broadcast(message, connection):
    for clients in client_sockets:
        if clients!=connection:
            try:
                clients.send(message)
            except:
                clients.close()
 
                remove(clients) 

# reverse hastable lookup to get the username
def get_connection_username(conn):
    for key in known_users:
        if known_users[key][0] == conn:
            return str(key)
    return "No found username for connection."


# remove a connection
def remove(connection):
    if connection in client_sockets:
        connection.send("You are being removed. Bye!")
        client_sockets.remove(connection)


# main function to parse wire protocol and respond accordingly
def handleMessage(message, conn, addr):
    # register a new user
    if message.startswith("USERNAME|"):
        list = message.split('|')
        username = list[1]
        if username not in known_users:
            known_users[username] = (conn, addr)
            print ("New user! Welcome " + username + " !")
        else:
            print("Returning user: " + username)

    # handle a general message
    elif message.startswith("MESSAGE|"):
        list = message.split("|")
        usernameFrom = list[1]
        usernameTo = list[2]
        msg = list[3]
        msgToSend = "<" + usernameFrom +"> " + msg
        if usernameTo in known_users:
            known_users[usernameTo][0].send(msgToSend)
        elif usernameTo == "TO_ALL":
            broadcast(msgToSend, conn)
        else:
            conn.send("User: " + username + " does not exist. Did not send message")

    # list all the current users
    elif message.startswith("LIST|"):
        print("requesting list of users: " + str(known_users))
        message_to_send = str(known_users.keys())
        conn.send(message_to_send)

    # delete a specified account
    elif message.startswith("DELETE|"):
        # parse message
        deleteAcct = message.split('|')
        cleanAcct = deleteAcct[1].split('\n')

        if cleanAcct[0] in known_users:
            connToRemove = known_users[str(cleanAcct[0])][0]
            remove(connToRemove) # remove from master list
            del known_users[str(cleanAcct[0])]
            message_to_send = "Removed account: " + str(cleanAcct[0])

            # Alert chatroom who was removed
            conn.send(message_to_send)
            broadcast(message_to_send, conn)
        else: 
            conn.send("Could not remove " + cleanAcct[0] + ". The user does not exist.")

    # base case for sending a normal message   
    else:
        username = get_connection_username(conn)
        print ("<" + username + "> " + message)

        # Calls broadcast function to send message to all
        message_to_send = "<" + username + "> " + message
        broadcast(message_to_send, conn)
 
while True:
    # Listen for new connections to accept
    client_socket, client_address = server.accept()
    logging.info(f"{client_address} has connected.")
    # Add the new client to connected sockets
    client_sockets.add(client_socket)
    # Create a thread for each client
    t = Thread(target=client_thread, args=(client_socket,))
    # Make the thread a daemon so it ends when the main thread does
    t.daemon = True
    # Start the thread
    t.start()

 
# clean up
conn.close()
server.close()
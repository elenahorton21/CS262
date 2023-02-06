import socket
import select
import sys
from _thread import *
 

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
 
 # maintain knowledge of all clients
list_of_clients = []
known_users = dict()
 
def clientthread(conn, addr):

    conn.send("Welcome to this chatroom!")
 
    while True:
            try:
                message = conn.recv(2048)
                if message:
                    handleMessage(message, conn, addr)
                else:
                    remove(conn)
            except:
                continue
 
def broadcast(message, connection):
    for clients in list_of_clients:
        if clients!=connection:
            try:
                clients.send(message)
            except:
                clients.close()
 
                remove(clients) 

# reverse hastable lookup to get the username
def get_connection_username(conn):
    for key in known_users:
        print(key)
        if known_users[key][0] == conn:
            return str(key)
    return "No found username for connection."


# remove a connection
def remove(connection):
    if connection in list_of_clients:
        conn.send("You are being removed. Bye!")
        list_of_clients.remove(connection)


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
    if message.startswith("MESSAGE|"):
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
 
    conn, addr = server.accept()
    list_of_clients.append(conn)
 
    # prints the address of the user that just connected
    print (addr[0] + " connected")
 
    # creates and individual thread for every user
    # that connects
    start_new_thread(clientthread,(conn,addr))    
 
conn.close()
server.close()
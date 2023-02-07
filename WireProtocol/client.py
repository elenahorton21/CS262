# Python program to implement client side of chat room.
import socket
import select
import sys

# simple function to register username
def registerUsername(username):
    usernameMsg = "USERNAME|" + username
    server.send(usernameMsg)
 
# set up socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# parse and check arguments
if len(sys.argv) != 4:
    print ("Correct usage: script, IP address, port number, username")
    exit()
IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
username = str(sys.argv[3])

# initialize connection with server
server.connect((IP_address, Port))
registerUsername(username)


# main function to create wire protocol from messages
def handleMessage(msg):
    # user requesting to list other users
    if msg.startswith("list"):
        return "LIST|\n"

    # user requesting to delete another user account
    elif msg.startswith("delete"):
        deleteAcct = msg.split(" ")
        return "DELETE|" + deleteAcct[1]

    # user requesting to send a direct message to a specified recipient
    elif msg.startswith(">>"):
        msgList = msg.split(":")
        usernameToSend1 = msgList[0].replace(">", "")
        usernameToSend = usernameToSend1.replace(" ", "")
        msgText = msgList[1]
        return "MESSAGE|" +  username +"|" + usernameToSend + "|" + msgText
   
   # user sending a general message to all
    else: 
        return "MESSAGE|"+ username+"|TO_ALL|" + msg
 
while True:
 
    # maintains a list of possible input streams
    sockets_list = [sys.stdin, server]
    read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])
 
    for socks in read_sockets:
        if socks == server:
            message = socks.recv(2048)
            print (message)
        else:
            message = sys.stdin.readline()
            msg = handleMessage(message)
            server.send(msg)
server.close()



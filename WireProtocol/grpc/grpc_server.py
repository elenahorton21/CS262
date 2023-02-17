from concurrent import futures

import grpc
import chat_pb2
import chat_pb2_grpc
from app import App
import logging
from config import config

chatServer = App()

# Logging config
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)


# Server config
SERVER_HOST = config["SERVER_HOST"]
SERVER_PORT = config["SERVER_PORT"]
MAX_BUFFER_SIZE = config["MAX_BUFFER_SIZE"]
MAX_NUM_CONNECTIONS = config["MAX_NUM_CONNECTIONS"]


class Chat(chat_pb2_grpc.ChatServicer):

    def create_user(self, request, _context):
        username = request.username
        print("Joining user: " + username)
        result = chatServer.create_user(username)
        response = str("Welcome to the chat " + username + "!")if result else str("Welcome back " + username + "!")
        return chat_pb2.ChatReply(message=response)

    # send message from one logged in user to another
    def send_message(self, request, _context):
        from_user = request.from_user
        to_user = request.to_user
        msg = request.message
        print("sending message from: " + from_user + " to: " + to_user)
        result = chatServer.send_message(from_user, to_user, msg)
        return chat_pb2.ChatReply(message = result)


    # list users matching with a wildcard
    def list_users(self, request, _context):
        wildcard = request.wildcard
        result = chatServer.list_users(wildcard)

        if result:
            return chat_pb2.ChatReply(message = result)
        else:
            return chat_pb2.ChatReply(message= "Could not list users.")

    # read a message that has been sent to the logged in user
    def get_message(self, request, _context):
        username = request.user
        msg = chatServer.get_messages(username)
        if msg == 100:
            return chat_pb2.ChatReply(message="LOGGED_OUT")
        else:
            return chat_pb2.ChatReply(message = msg)

    # delete user
    def delete_user(self, request, _context):
        user_to_delete = request.to_user
        user_deleting = request.from_user
        response = chatServer.delete_user(user_to_delete, user_deleting)
        if response == True:
            print("User " + user_to_delete + " deleted by " + user_deleting)
            response = "Success."
        return chat_pb2.ChatReply(message = response)



def serve():
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    chat_pb2_grpc.add_ChatServicer_to_server(Chat(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("GRPC Server started, listening on " + port)
    server.wait_for_termination()



####-------------------------------------------------------------------####


# def _handle_chat_message(user, to_user, msg, app):
#     """
#     Handle a ChatMessage from client. Returns an error response if the recipient
#     does not exist. Otherwise, broadcasts to active recipients, queues the 
#     the message for inactive recipients, and returns a success response.

#     Args:
#         msg (ChatMessage): The message received from client.
#         app (AppState): The current app state.
    
#     Returns:
#         ChatResponse: The response to client.
#     """
#     # If the recipient does not exist, return an error response
#     if to_user and not app.is_valid_user(to_user):
#         res = str("User " + to_user + " does not exist.")
#         return res

#     # Convert ChatMessage to BroadcastMessage
#     broadcast_msg = msg.to_broadcast() 
#     # If recipient was not specified, all active users are recipients
#     if not to_user:
#         recv_conns = app.get_all_connections()
#     # Otherwise, broadcast the message to sender, and recipient if active.
#     else:
#         # TODO: Roundabout way of getting sender socket    
#         recv_conns = [app.get_user_connection(user)]
#         # Get recipient socket
#         recipient_conn = app.get_user_connection(to_user)
#         # If recipient is active, add their socket to receiving connections
#         if recipient_conn:
#             recv_conns.append(recipient_conn)
#         # If `recv_conn` is None, the user is inactive. Queue the message for later.
#         else:
#             app.queue_message(to_user, broadcast_msg)
    
#     # Broadcast the message to recipients
#     # TODO: Are there cases where this fails and we should return error response?
#     broadcast(broadcast_msg, recv_conns)

#     # Return success response
#     return True

# def broadcast(msg, recvs):
#     """
#     Send a message to a list of clients.
#     TODO: Handle exceptions with `conn.send`.

#     Args:
#         msg (BroadcastMessage): The message to send to clients.
#         recvs (List[Socket]): The sockets to send the message to.

#     Returns:
#         None
#     """
#     # Check that the message is an instance of BroadcastMessage

#     for conn in recvs:
#         conn.send(msg.encode_())

if __name__ == '__main__':
    serve()



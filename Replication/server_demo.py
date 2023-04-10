from concurrent import futures

import sys
import grpc
import time
import threading
from config import config

import proto.chat_pb2 as chat
import proto.chat_pb2_grpc as rpc

from server import Replica, ChatServer

if __name__ == '__main__':
    address = config["SERVER_HOST"]
    replicas = [Replica(address, 5002), Replica(address, 5003), Replica(address, 5004)]
    # Simple loop to initialize ChatServer instances with the appropriate parent replicas
    parents = []
    servers = []
    for ind, repl in enumerate(replicas):
        if ind == int(sys.argv[1]):
            server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # Create a gRPC server
            is_primary = (len(parents) == 0) # Set the first to the primary
            rpc.add_ChatServicer_to_server(ChatServer(parent_replicas=parents, is_primary=is_primary), server)  # Register the server to gRPC
            print('Starting server. Listening...')
            server.add_insecure_port('[::]:' + str(repl.port))
            server.start()
            servers.append(server)
        parents.append(repl)

    for ind, server in enumerate(servers):
        server.wait_for_termination()

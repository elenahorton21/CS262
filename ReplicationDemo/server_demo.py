from concurrent import futures

import sys
import grpc
import time
import threading

import proto.chat_pb2 as chat
import proto.chat_pb2_grpc as rpc

from server import Replica, ChatServer

if __name__ == '__main__':
    address = "0.0.0.0"
    replicas = [Replica(address, 5002), Replica(address, 5003), Replica(address, 5004)]
    # Simple loop to initialize ChatServer instances with the appropriate parent replicas
    parents = []
    servers = []
    for ind, repl in enumerate(replicas):
        # the workers is like the amount of threads that can be opened at the same time, when there are 10 clients connected
        # then no more clients able to connect to the server.
        if ind == int(sys.argv[1]):
            server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # create a gRPC server
            is_primary = (len(parents) == 0) # Set the first to the primary
            rpc.add_ReplicaServiceServicer_to_server(ChatServer(parent_replicas=parents, is_primary=is_primary), server)  # register the server to gRPC
            # gRPC basically manages all the threading and server responding logic, which is perfect!
            print('Starting server. Listening...')
            server.add_insecure_port('[::]:' + str(repl.port))
            server.start()
            servers.append(server)
        parents.append(repl)

    for ind, server in enumerate(servers):
        server.wait_for_termination()

    # curr_ind = 0
    # while curr_ind < 3:
    #     time.sleep(5)
    #     print(f"Stopping server {curr_ind}")
    #     servers[curr_ind].stop(grace=None)
    #     curr_ind += 1

    # # Server starts in background (in another thread) so keep waiting
    # # if we don't wait here the main thread will end, which will end all the child threads, and thus the threads
    # # from the server won't continue to work and stop the server
    # while True:
    #     time.sleep(64 * 64 * 100)
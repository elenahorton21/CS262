from concurrent import futures

import grpc
import time
import threading

import proto.chat_pb2 as chat
import proto.chat_pb2_grpc as rpc


class Replica:
    def __init__(self, address, port):
        self.address = address
        self.port = port


class ChatServer(rpc.ReplicaServiceServicer):  # inheriting here from the protobuf rpc file which is generated
    def __init__(self, parent_replicas=[], is_primary=False):
        self.state = 0 # Test value, can ignore
        self.parent_replicas = parent_replicas
        self.server_id = len(parent_replicas) # 0, 1, 2
        self.is_primary = is_primary
        self.state_updates = []        

        # Create a connection for each parent replica
        self.conns = {}
        for ind, replica in enumerate(self.parent_replicas):
            channel = grpc.insecure_channel(replica.address + ':' + str(replica.port))
            conn = rpc.ReplicaServiceStub(channel)
            self.conns[ind] = conn
            threading.Thread(target=self.__listen_for_state_updates, args=(ind,), daemon=True).start()

            # Subscribe to channel connectivity. Maybe combine this with self.conns so failed channels are removed. Then we 
            # can use this to know when `self` is the primary.
            channel.subscribe(lambda event: self.__channel_connectivity_callback(event, ind))

    # TODO: This is never called when I exit the program on Terminal.
    def __channel_connectivity_callback(self, event, conn_ind):
        print("Callback called")
        # Remove the channel from self.conns
        if event == grpc.ChannelConnectivity.SHUTDOWN:
            print(f"Connection to server {conn_ind} ended.")
            del self.conns[conn_ind]

        # If no connections remain, set self to primary
        if not self.conns:
            self.is_primary = True

    def __listen_for_state_updates(self, conn_ind):
        """
        conn_ind (int): The index of the connection
        """
        try:
            for val in self.conns[conn_ind].StateUpdateStream(chat.Empty()):
                print(f"Server {self.server_id} received message: {val}")
                self.state = int(val.test)
        except Exception as e:
            print("Error occurred")
            print(e)
            del self.conns[conn_ind]

            # If no connections remain, set self to primary
            if not self.conns:
                self.is_primary = True
                print(f"Server {self.server_id} is now the primary.")

            return

    # The stream which will be used to send state updates to child_replica.
    def HeartbeatStream(self, request, context):
        """
        This is a response-stream type call. This means the server can keep sending messages
        Every client opens this connection and waits for server to send new messages
        :param request_iterator:
        :param context:
        :return:
        """
        # For every client a infinite loop starts (in gRPC's own managed thread)
        n = 0
        while True:
            # Only primary sends state updates
            if self.is_primary:
                n += 1                    
                yield chat.Heartbeat(timestamp=str(n))
            time.sleep(1)

    # TODO: Modify so that updates are removed from `self.state_updates` when they are yielded.
    def StateUpdateStream(self, request, context):
        while True:
            for update in self.state_updates:
                yield update

if __name__ == '__main__':
    address = "0.0.0.0"
    replicas = [Replica(address, 5002), Replica(address, 5003), Replica(address, 5004)]
    # Simple loop to initialize ChatServer instances with the appropriate parent replicas
    parents = []
    servers = []
    for repl in replicas:
        # the workers is like the amount of threads that can be opened at the same time, when there are 10 clients connected
        # then no more clients able to connect to the server.
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # create a gRPC server
        is_primary = (len(parents) == 0) # Set the first to the primary
        rpc.add_ReplicaServiceServicer_to_server(ChatServer(parent_replicas=parents, is_primary=is_primary), server)  # register the server to gRPC
        # gRPC basically manages all the threading and server responding logic, which is perfect!
        print('Starting server. Listening...')
        server.add_insecure_port('[::]:' + str(repl.port))
        server.start()
        servers.append(server)
        parents.append(repl)

    # for ind, server in enumerate(servers):
    #     server.wait_for_termination()

    curr_ind = 0
    while curr_ind < 3:
        time.sleep(5)
        print(f"Stopping server {curr_ind}")
        servers[curr_ind].stop(grace=None)
        curr_ind += 1

    # # Server starts in background (in another thread) so keep waiting
    # # if we don't wait here the main thread will end, which will end all the child threads, and thus the threads
    # # from the server won't continue to work and stop the server
    # while True:
    #     time.sleep(64 * 64 * 100)
# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import chat_pb2 as chat__pb2


class ChatStub(object):
    """defining our chat service
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.create_user = channel.unary_unary(
                '/chat.Chat/create_user',
                request_serializer=chat__pb2.UserRequest.SerializeToString,
                response_deserializer=chat__pb2.ChatReply.FromString,
                )
        self.list_users = channel.unary_unary(
                '/chat.Chat/list_users',
                request_serializer=chat__pb2.ListRequest.SerializeToString,
                response_deserializer=chat__pb2.ChatReply.FromString,
                )
        self.delete_user = channel.unary_unary(
                '/chat.Chat/delete_user',
                request_serializer=chat__pb2.DeleteRequest.SerializeToString,
                response_deserializer=chat__pb2.ChatReply.FromString,
                )
        self.send_message = channel.unary_unary(
                '/chat.Chat/send_message',
                request_serializer=chat__pb2.MessageRequest.SerializeToString,
                response_deserializer=chat__pb2.ChatReply.FromString,
                )
        self.get_message = channel.unary_unary(
                '/chat.Chat/get_message',
                request_serializer=chat__pb2.GetRequest.SerializeToString,
                response_deserializer=chat__pb2.ChatReply.FromString,
                )
        self.chat_stream = channel.unary_stream(
                '/chat.Chat/chat_stream',
                request_serializer=chat__pb2.MessageRequest.SerializeToString,
                response_deserializer=chat__pb2.ChatReply.FromString,
                )
        self.logout_user = channel.unary_unary(
                '/chat.Chat/logout_user',
                request_serializer=chat__pb2.UserRequest.SerializeToString,
                response_deserializer=chat__pb2.ChatReply.FromString,
                )
        self.StateUpdateStream = channel.unary_stream(
                '/chat.Chat/StateUpdateStream',
                request_serializer=chat__pb2.Empty.SerializeToString,
                response_deserializer=chat__pb2.StateUpdate.FromString,
                )
        self.HeartbeatStream = channel.unary_stream(
                '/chat.Chat/HeartbeatStream',
                request_serializer=chat__pb2.Empty.SerializeToString,
                response_deserializer=chat__pb2.Heartbeat.FromString,
                )
        self.check_connection = channel.unary_unary(
                '/chat.Chat/check_connection',
                request_serializer=chat__pb2.Empty.SerializeToString,
                response_deserializer=chat__pb2.Empty.FromString,
                )


class ChatServicer(object):
    """defining our chat service
    """

    def create_user(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def list_users(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def delete_user(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def send_message(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def get_message(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def chat_stream(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def logout_user(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StateUpdateStream(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def HeartbeatStream(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def check_connection(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ChatServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'create_user': grpc.unary_unary_rpc_method_handler(
                    servicer.create_user,
                    request_deserializer=chat__pb2.UserRequest.FromString,
                    response_serializer=chat__pb2.ChatReply.SerializeToString,
            ),
            'list_users': grpc.unary_unary_rpc_method_handler(
                    servicer.list_users,
                    request_deserializer=chat__pb2.ListRequest.FromString,
                    response_serializer=chat__pb2.ChatReply.SerializeToString,
            ),
            'delete_user': grpc.unary_unary_rpc_method_handler(
                    servicer.delete_user,
                    request_deserializer=chat__pb2.DeleteRequest.FromString,
                    response_serializer=chat__pb2.ChatReply.SerializeToString,
            ),
            'send_message': grpc.unary_unary_rpc_method_handler(
                    servicer.send_message,
                    request_deserializer=chat__pb2.MessageRequest.FromString,
                    response_serializer=chat__pb2.ChatReply.SerializeToString,
            ),
            'get_message': grpc.unary_unary_rpc_method_handler(
                    servicer.get_message,
                    request_deserializer=chat__pb2.GetRequest.FromString,
                    response_serializer=chat__pb2.ChatReply.SerializeToString,
            ),
            'chat_stream': grpc.unary_stream_rpc_method_handler(
                    servicer.chat_stream,
                    request_deserializer=chat__pb2.MessageRequest.FromString,
                    response_serializer=chat__pb2.ChatReply.SerializeToString,
            ),
            'logout_user': grpc.unary_unary_rpc_method_handler(
                    servicer.logout_user,
                    request_deserializer=chat__pb2.UserRequest.FromString,
                    response_serializer=chat__pb2.ChatReply.SerializeToString,
            ),
            'StateUpdateStream': grpc.unary_stream_rpc_method_handler(
                    servicer.StateUpdateStream,
                    request_deserializer=chat__pb2.Empty.FromString,
                    response_serializer=chat__pb2.StateUpdate.SerializeToString,
            ),
            'HeartbeatStream': grpc.unary_stream_rpc_method_handler(
                    servicer.HeartbeatStream,
                    request_deserializer=chat__pb2.Empty.FromString,
                    response_serializer=chat__pb2.Heartbeat.SerializeToString,
            ),
            'check_connection': grpc.unary_unary_rpc_method_handler(
                    servicer.check_connection,
                    request_deserializer=chat__pb2.Empty.FromString,
                    response_serializer=chat__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'chat.Chat', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Chat(object):
    """defining our chat service
    """

    @staticmethod
    def create_user(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chat.Chat/create_user',
            chat__pb2.UserRequest.SerializeToString,
            chat__pb2.ChatReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def list_users(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chat.Chat/list_users',
            chat__pb2.ListRequest.SerializeToString,
            chat__pb2.ChatReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def delete_user(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chat.Chat/delete_user',
            chat__pb2.DeleteRequest.SerializeToString,
            chat__pb2.ChatReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def send_message(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chat.Chat/send_message',
            chat__pb2.MessageRequest.SerializeToString,
            chat__pb2.ChatReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def get_message(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chat.Chat/get_message',
            chat__pb2.GetRequest.SerializeToString,
            chat__pb2.ChatReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def chat_stream(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/chat.Chat/chat_stream',
            chat__pb2.MessageRequest.SerializeToString,
            chat__pb2.ChatReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def logout_user(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chat.Chat/logout_user',
            chat__pb2.UserRequest.SerializeToString,
            chat__pb2.ChatReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def StateUpdateStream(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/chat.Chat/StateUpdateStream',
            chat__pb2.Empty.SerializeToString,
            chat__pb2.StateUpdate.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def HeartbeatStream(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/chat.Chat/HeartbeatStream',
            chat__pb2.Empty.SerializeToString,
            chat__pb2.Heartbeat.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def check_connection(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chat.Chat/check_connection',
            chat__pb2.Empty.SerializeToString,
            chat__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

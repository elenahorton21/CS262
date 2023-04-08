from .app import App, User, Message
from .grpc_server import Chat
import unittest
from unittest.mock import patch

class MockGRPCServerReply:
    def __init__(self, response):
        self.response = response

class MockUserRequest:
    def __init__(self, username):
        self.username = username

class MockGetRequest:
    def __init__(self, user):
        self.user = user

class MockDeleteRequest:
    def __init__(self, from_user, to_user):
        self.from_user = from_user
        self.to_user = to_user

class MockMessageRequest:
    def __init__(self, from_user, to_user, message):
        self.from_user = from_user
        self.to_user = to_user
        self.message = message

class MockListRequest:
    def __init__(self, wildcard):
        self.wildcard = wildcard

class MockChatReply:
    def __init__(self, message):
       self.message = message

    def ChatReply(self, message):
        self.message = message

class GRPCTest(unittest.TestCase):
    
    def setUp(self):
        self.app = App()
        self.username = "elena"
        self.user2 = "jerry"
        self.user3 = "newbie"
        self.user = User(self.username)
        self.message = "hello world!"  

     # App tests--> App, User, and Message classes
    
    
    def test_App(self):

        # test creating users in the App class
        self.app.create_user(self.username)
        self.app.create_user(self.user2)
        self.app.create_user(self.user3)
    
        # make sure the users list is accurate
        app_users = list(self.app.users.keys())
        self.assertEqual(["elena", "jerry", "newbie"], app_users)

        # test sending a message to all
        self.app.send_message(self.username, None, self.message)

        # test message class creation
        self.assertEqual(self.app.users[self.user2].messages[0].from_user, "elena")
        self.assertEqual(self.app.users[self.user2].messages[0].message, "hello world!")

        # message should be in both other users message queues, but not elena's
        jerry_msgs = self.app.users.get(self.user2).messages
        newbie_msgs = self.app.users.get(self.user3).messages
        elena_msgs = self.app.users.get(self.username).messages
        self.assertEqual(1, len(jerry_msgs))
        self.assertEqual(1, len(newbie_msgs))
        self.assertEqual(0, len(elena_msgs))

        # test sending message to a specific user (elena --> jerry)
        self.app.send_message(self.username, self.user2, self.message)

        # message should be in jerry's queue but not elena's or newbie's
        jerry_msgs = self.app.users.get(self.user2).messages
        newbie_msgs = self.app.users.get(self.user3).messages
        elena_msgs = self.app.users.get(self.username).messages
        self.assertEqual(2, len(jerry_msgs))
        self.assertEqual(1, len(newbie_msgs))
        self.assertEqual(0, len(elena_msgs))


        # test getting messages
            # elena has no message
        self.assertEqual("NONE", self.app.get_messages(self.username))
            # both of jerry's messages are "hello world!" from elena
        self.assertEqual("elena: hello world!", self.app.get_messages(self.user2))
        self.assertEqual("elena: hello world!", self.app.get_messages(self.user2))
            # newbie should have only one message from elena
        self.assertEqual("elena: hello world!", self.app.get_messages(self.user3))
        self.assertEqual("NONE", self.app.get_messages(self.user3))
            # test an unknown username returning error 100
        self.assertEqual(100, self.app.get_messages("fakeUser"))

        # test deleting a user
        self.assertEqual(3, len(self.app.users))
        self.app.delete_user(self.user3, self.username)
        self.assertEqual(2, len(self.app.users))
        users_list = list(self.app.users.keys())
        self.assertEqual(['elena', 'jerry'], users_list)
    
        # test listing users
        self.assertEqual("elena, jerry, ", self.app.list_users("")) # with no wildcard
        self.assertEqual("elena, ", self.app.list_users("e")) # with just e wildcard, should return elena
        self.assertEqual("jerry, ", self.app.list_users(".*r")) # with r wildcard anywhere in the name
        self.assertEqual("", self.app.list_users("b")) # no matching users
    
    def test_User(self):
        user = User(self.username)
        self.assertEqual(self.username, user.username)
        self.assertEqual(True, user.logged_in)
        self.assertEqual([], user.messages)

        # test adding a message to the user queue
        user.add_message(self.message)
        self.assertEqual(1, len(user.messages))
        self.assertEqual(["hello world!"], user.messages) 

        # test logging in and logging out user
        user.log_out()
        self.assertEqual(False, user.logged_in)
        user.log_in()
        self.assertEqual(True, user.logged_in)

    def test_Message(self):
        msg = Message(self.username, self.message)
        self.assertEqual(self.username, msg.from_user)
        self.assertEqual(self.message, msg.message)

    def test_grpc(self):

        with patch('chat_pb2') as mock_server_reply:
            mock_server_reply.ChatReply.message = MockChatReply(mock_server_reply.message)
            grpc_server = Chat()

            # Registering a user: 3 cases to test
            # Case 1: register a new user
            user_request = MockUserRequest(self.username)
            self.assertEqual("SUCCESS", grpc_server.create_user(user_request, "").message)

            # case 2: try to register a user that already exists, repeat the call, different response
            self.assertEqual("This username is already logged in. Please choose another one.", grpc_server.create_user(user_request, "").message)

            # try to logout the user
            self.assertEqual("SUCCESS", grpc_server.logout_user(user_request, "").message)

            # Case 3: now try to return as the same user
            self.assertEqual("Welcome back " + self.username + " !", grpc_server.create_user(user_request, "").message)

            ##---- Sending a message: 3 cases to test ---##

            # first, create two new users
            user_request2 = MockUserRequest(self.user2)
            user_request3 = MockUserRequest(self.user3)
            self.assertEqual("SUCCESS", grpc_server.create_user(user_request2, "").message)
            self.assertEqual("SUCCESS", grpc_server.create_user(user_request3, "").message)
            
            # Case 1: Send a message to all
            message_request = MockMessageRequest(from_user=self.username, to_user=None, message=self.message)
            self.assertEqual("Success",grpc_server.send_message(message_request, "").message)

            # Case 2: Send a message to a specific user
            message_request = MockMessageRequest(from_user=self.username, to_user=self.user2, message=self.message)
            self.assertEqual("Success",grpc_server.send_message(message_request, "").message)

            # Case 3: Send a message to a user that doesn't exist
            message_request = MockMessageRequest(from_user=self.username, to_user="fakeUser", message=self.message)
            self.assertEqual("Error: User fakeUser does not exist.",grpc_server.send_message(message_request, "").message)

            # Test listing users, 3 cases

            # test listing all users
            message_request = MockListRequest(wildcard="")
            self.assertEqual("elena, jerry, newbie, ", grpc_server.list_users(message_request, "").message)

            # test listing with existing wildcard
            message_request = MockListRequest(wildcard=".*r")
            self.assertEqual("jerry, ", grpc_server.list_users(message_request, "").message)

            # test listing with no matching users
            message_request = MockListRequest(wildcard=".*z")
            self.assertEqual("No users to list.", grpc_server.list_users(message_request, "").message)

            # Test deleting a user, 2 cases

            # test deleting a user that doesn't exist
            delete_request = MockDeleteRequest(self.username, "fakeUser")
            self.assertEqual("Error: User fakeUser does not exist.", grpc_server.delete_user(delete_request, "").message)

            # test deleting a known user
            delete_request = MockDeleteRequest(self.username, self.user3)
            self.assertEqual("Success.", grpc_server.delete_user(delete_request, "").message)


            # test getting messages, 3 cases (logged in vs. logged out and no messages)

            # logged in, getting messages (should have 2 messages from elena)
            get_request = MockGetRequest(self.user2)
            self.assertEqual(self.username + ": " + self.message, grpc_server.get_message(get_request, "").message)

            # logged in, should have no messages
            get_request = MockGetRequest(self.username)
            self.assertEqual("NONE", grpc_server.get_message(get_request, "").message)

            # logged out
            user_request = MockUserRequest(self.username)
            self.assertEqual("SUCCESS", grpc_server.logout_user(user_request, "").message)
            
            get_request = MockGetRequest(self.username)
            self.assertEqual("LOGGED_OUT", grpc_server.get_message(get_request, "").message)





            



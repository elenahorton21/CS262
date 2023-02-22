from app import App, User, Message
from grpc_server import Chat
import unittest

class MockGRPCServerReply:
    def __init__(self, response):
        self.response = response

class MockUserRequest:
    def __init__(self, username):
        self.username = username

class MockMessageRequest:
    def __init__(self, user_from, user_to, message):
        self.user_from = user_from
        self.user_to = user_to
        self.message = message

class MockChatReply:
    def __init__(self):
       self.message = ""

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


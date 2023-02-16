import re

# holds the overall state of the application--> users and their message lists, allows the server to delete, list, and send messages
class App:
    def __init__(self):
        self.users = {}

    # Adds a new user to the memory manager
    def create_user(self, username):
        if username not in self.users:
            self.users[username] = User(username)
            return True
        else:
            return False

 
 # A user contains the user's username and their list of messages
class User:
    def __init__(self, username):
        self.username = username
        self.messages = []

    # appends a message to the list of messages
    def add_message(self, message):
        self.messages.append(message)
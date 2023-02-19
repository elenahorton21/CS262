import re

# holds the overall state of the application--> users and their message lists, allows the server to delete, list, and send messages
class App:
    def __init__(self):
        self.users = {}

    # Adds a new user to the memory manager
    def create_user(self, username):
        if username not in self.users:
            self.users[username] = User(username)
            return 0
        elif username in self.users and self.users[username].logged_in == True:
            return 1
        else:
            return 2
    
    def send_message(self, from_user, to_user, message):
        msg = Message(from_user, message)
        if from_user not in self.users:
            return "Error: You are not an active user. Please log in."
        
        # if the user the message is being sent to does not exist
        if to_user and to_user not in self.users:
            return str("Error: User " + to_user + " does not exist.")
        
        # sending to a specific user and they exist
        elif to_user:
            user_to_send = self.users[to_user]
            user_to_send.add_message(msg)

        # broadcasting to all users 
        else:
            for u in self.users:
                if u != from_user:
                    self.users[u].add_message(msg)
                    print ("adding message to " + u + " 's queue")
        return "Success"

    
    def get_messages(self, username):
        if username not in self.users:
            return 100
        elif len(self.users[username].messages) == 0:
            return "NONE"
        
        # limitation: can only respond one message at a time
        else:
            if len(self.users[username].messages) > 0:
                msg = self.users[username].messages.pop(0)
                print("msg in queue!--> " + msg.message)
                from_user = msg.from_user
                msgText = msg.message
            return str(from_user + ": " + msgText)

    def list_users(self, wildcard):
        response = ""
        try:
            matchedUsers = [user for user in self.users if re.match(wildcard, user)]
            print(matchedUsers)
            for user in matchedUsers:
                response += str(self.users[user].username + ", ")
        except Exception:
            "BAD WILDCARD SEARCH TERM"
            response = "Improper Wildcard Term"
        return response

    def delete_user(self, user_to_delete, user_deleting):
        if user_to_delete not in self.users:
            return ("Error: User " + user_to_delete +" does not exist.")
        elif user_deleting not in self.users:
            return ("Error: Not authorized to delete.")
        else:
            self.send_message(user_deleting, user_to_delete, "You have been deleted by me.")
            self.users.pop(user_to_delete)
            return True
    
    def logout_user(self, username):
        if username not in self.users:
            return False
        else:
            self.users[username].log_out()
            return True


 
 # A user contains the user's username and their list of messages
class User:
    def __init__(self, username):
        self.username = username
        self.logged_in = True
        self.messages = []

    # appends a message to the list of messages
    def add_message(self, message):
        self.messages.append(message)
    
    def log_out(self):
        self.logged_in = False
    
    def log_in(self):
        self.logged_in = True
        

class Message:
    def __init__(self, from_user, msg):
        self.from_user = from_user
        self.message = msg
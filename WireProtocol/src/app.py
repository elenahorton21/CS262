"""
Defines logic for chat application state.

TODO: Might want to make fields `private` and use getter/setter methods. Could
be cleaner with the locking as well.
"""


class AppState:
  def __init__(self):
    self.users = set() # String array of usernames
    self.connections = {} # Map of users to connections
    self.msg_queue = {} # Map of users to messsages (str array)

  def _get_connection_username(self, conn):
    for key, value in self.connections.items():
      if value == conn:
        return key

    raise ValueError("No username found for connection")

  def register_user(self, username):
    if username in self.users:
      raise ValueError("Username is already registered.")
    elif not username.isalnum():
      raise ValueError("Username must contain alphanumeric characters only.")
    else:
      self.users.add(username)

  def add_connection(self, username, socket):
    """
    Returns False if the connection is a previous user logging in, so 
    the server can send the message queue.
    """
    # 1) username is new
    if username not in self.users:
        self.register_user(username)
        self.connections[username] = socket
        return False
    # 2) username is currently being used
    elif username in self.connections.keys():
        raise ValueError("Username is currently being used.")
    # 3) username exists and not being used
    else:
        self.connections[username] = socket
        return True

  def remove_connection(self, socket):
    """Remove the connection from self.connections."""
    username = self._get_connection_username(socket)
    self.connections.pop(username)

  def queue_message(self, username, msg):
    if username not in self.users:
      raise ValueError("Username does not exist.")
    
    # Add the text to the user's message queue
    if username in self.msg_queue:
      self.msg_queue[username].append(msg)
    else:
      self.msg_queue[username] = [msg]


# class SafeAppState extends AppState with lock functionality
# https://www.bogotobogo.com/python/Multithread/python_multithreading_Synchronization_Lock_Objects_Acquire_Release.php

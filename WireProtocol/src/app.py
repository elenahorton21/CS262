"""
Defines logic for chat application state.

TODO: Might want to make fields `private` and use getter/setter methods. Could
be cleaner with the locking as well.
TODO: Clean up and organize methods.
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

  def get_all_connections(self):
    """Return sockets for all active users."""
    return list(self.connections.values())

  def get_user_connection(self, username):
    """Return the socket for username or raise a KeyError."""
    try:
      return self.connections[username]
    except KeyError as _:
      # If the user is not in users, return None
      return None
  
  def list_users(self):
    return list(self.users)
  
  def is_valid_user(self, username):
    """
    Returns True if username is registered, regardless of whether there 
    is an active connection.
    """
    return (username in self.users)
  
  def register_user(self, username):
    if username in self.users:
      raise ValueError("Username is already registered.")
    elif not username.isalnum():
      raise ValueError("Username must contain alphanumeric characters only.")
    else:
      self.users.add(username)

  def delete_user(self, username):
    """
    Remove the username from the list of users and from message queue.
    TODO: Decide how to handle the case where user is active, i.e. in 
    self.connections.
    """
    self.users.remove(username)
    self.msg_queue.pop(username)

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
    """
    Queue a message to be delivered when the user logs in.

    Args:
        username (str): The username of the recipient.
        msg (BroadcastMessage): The message to deliver.

    Returns:
        None
    """
    if username not in self.users:
      raise ValueError("Username does not exist.")
    
    # Add the text to the user's message queue
    if username in self.msg_queue:
      self.msg_queue[username].append(msg)
    else:
      self.msg_queue[username] = [msg]


# class SafeAppState extends AppState with lock functionality
# https://www.bogotobogo.com/python/Multithread/python_multithreading_Synchronization_Lock_Objects_Acquire_Release.php

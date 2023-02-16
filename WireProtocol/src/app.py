"""
Defines logic for chat application state. AppState stores registered usernames,
active connections, and queued messages for inactive users.

TODO: Implement locking for race conditions in SafeAppState class.
"""


class InvalidUserError(Exception):
    """Raised in cases where the username is invalid, i.e. not registered."""
    pass


class AppState:
    def __init__(self, users=set(), connections={}, msg_queue={}):
        """
        Initialize AppState.
        
        Args:
            users (Set[str], optional): Set of username strings.
            connections (Dict[str, Socket], optional): Map of usernames to active socket connections.
            msg_queue (Dict[str, List[str]], optional): Map of usernames to queued messages in string format.
        """
        self._users = users 
        self._connections = connections 
        self._msg_queue = msg_queue 

    def _get_connection_username(self, conn):
        """Return the username that the connection is logged in as."""
        for key, value in self._connections.items():
            if value == conn:
                return key

        raise KeyError("No user found for connection.")
    
    def is_valid_user(self, username):
        """Returns True if username is registered."""
        return (username in self._users)
    
    def get_all_connections(self):
        """Return sockets for all active users."""
        return list(self._connections.values())

    def get_user_connection(self, username):
        """
        Return the socket for username or None if the user is inactive.
        
        Args:
            username (str): The username.
        
        Returns:
            Union[Socket, None]: The socket connection for the username or
                None if the user is inactive.
        
        Raises:
            InvalidUserError: If the username is not registered.
        """
        if not self.is_valid_user(username):
            raise InvalidUserError()
        
        return self._connections.get(username, None)
  
    def list_users(self):
        """Return a list of all registered usernames."""
        return list(self._users)
  
    def register_user(self, username):
        """Register a new username."""
        if username in self._users:
            raise ValueError("Username is already registered.")
        elif not username.isalnum():
            raise ValueError("Username must contain only alphanumeric characters only.")
        else:
            self._users.add(username)

    def delete_user(self, username):
        """
        Remove the username from the list of users and from message queue.
        TODO: Decide how to handle the case where user is active, i.e. in 
        self.connections.

        Args:
            username (str): The user to delete.

        Returns:
            None

        Raises:
            InvalidUserError: If user is not registered.
        """
        if not self.is_valid_user(username):
            raise InvalidUserError
        
        self._users.remove(username)
        self._msg_queue.pop(username)

    def add_connection(self, username, socket):
        """
        Returns False if the connection is a previous user logging in, so 
        the server can send the message queue.

        TODO: We could add a check that the socket isn't logged in with
        multiple usernames.
        """
        # Username is currently being used
        if username in self._connections.keys():
            raise ValueError("Username is currently being used.")
        # If username exists and is inactive, add an active connection
        elif self.is_valid_user(username):
            self._connections[username] = socket
            return True
        # Otherwise, try to register a new username. This may
        # raise an exception.
        else:
            self.register_user(username)
            self._connections[username] = socket
            return False

    def remove_connection(self, socket):
        """Remove the connection from self.connections."""
        username = self._get_connection_username(socket)
        self._connections.pop(username)

    def queue_message(self, username, msg):
        """
        Queue a message to be delivered when the user logs in.

        Args:
            username (str): The username of the recipient.
            msg (BroadcastMessage): The message to deliver.

        Returns:
            None

        Raises:
            InvalidUserError: If the user is not registered.
        """
        if not self.is_valid_user(username):
            raise InvalidUserError()
        
        # Add the text to the user's message queue
        if username in self._msg_queue:
            self._msg_queue[username].append(msg)
        else:
            self._msg_queue[username] = [msg]


# class SafeAppState extends AppState with lock functionality
# https://www.bogotobogo.com/python/Multithread/python_multithreading_Synchronization_Lock_Objects_Acquire_Release.php

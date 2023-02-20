"""
Defines logic for chat application state. AppState stores registered usernames,
active connections, and queued messages for inactive users.

TODO: Implement locking for race conditions in SafeAppState class.
"""

class InvalidUserError(Exception):
    """Raised in cases where the username is invalid, i.e. not registered."""
    def __init__(self, msg='Username is not registered.', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


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
  
    def list_users(self, wildcard=None):
        """
        Return a list of all registered usernames.
        TODO: Handle wildcards.
        """
        return list(self._users)
  
    def register_user(self, username):
        """
        Register a username.

        Returns:
            bool: True if the user is new, False if registering with
                an existing username.
        
        Raises:
            ValueError: If the username contains non-alphanumeric characters.
            InvalidUserError: If the username is being used by an active user.
        """
        if username in self._connections.keys():
            raise InvalidUserError("Username is already in use.")
        elif not username.isalnum():
            raise ValueError("Username must contain only alphanumeric characters only.")
        
        # Check if the user is a previously registered username
        if username in self._users:
            return False
        else:
            self._users.add(username)
            return True

    def delete_user(self, username):
        """
        Remove the username from the list of users and from message queue.

        Args:
            username (str): The user to delete.

        Returns:
            None

        Raises:
            InvalidUserError: If user is not registered.
            ValueError: If user is active.
        """
        # Raise an error if username is not registered or is active
        if not self.is_valid_user(username):
            raise InvalidUserError(f"Username '{username}' is not registered.")
        if self.get_user_connection(username):
            raise ValueError("Cannot delete an active user.")
        
        self._users.remove(username)
        self._msg_queue.pop(username, None) # Pass a default so that KeyError is not raised

    def add_connection(self, username, socket):
        """Create an active connection for `username` to socket."""
        # Check that there is not already an active connection with username
        if username in self._connections.keys():
            raise InvalidUserError("Username is already connected to a socket.")
        # Check that the socket is not already registered to a user
        if socket in self._connections.values():
            raise ValueError("Socket is already associated with another user.")

        self._connections[username] = socket

    def remove_connection(self, socket):
        """Remove the socket from active connections."""
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

    def get_queued_messages(self, username):
        """
        Return the queued messages for the user.
        
        Args:
            username (str): The user's username.
        
        Returns:
            List[BroadcastMessage]: The messages in the user's message queue.
        
        Raises:
            InvalidUserError: If the user is not registered.
        """
        if not self.is_valid_user(username):
            raise InvalidUserError()
        
        # If no messages, return empty list
        return self._msg_queue.get(username, [])

# class SafeAppState extends AppState with lock functionality
# https://www.bogotobogo.com/python/Multithread/python_multithreading_Synchronization_Lock_Objects_Acquire_Release.php

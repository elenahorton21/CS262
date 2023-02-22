"""
Basic implementation for configuration values shared across client and server.
"""

config = {
    "MAX_BUFFER_SIZE": 1024,
    "MAX_NUM_CONNECTIONS": 10,
    "SERVER_HOST": "0.0.0.0", # Address the server binds to
    "SERVER_PORT": 5002,
    "SERVER_ADDRESS": "192.168.1.220", # The IP address of the server
    "DEBUG_SERVER_ADDRESS": "0.0.0.0", # The localhost
    "DEBUG": True
}
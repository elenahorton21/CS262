"""
Basic implementation for configuration values shared across client and server.
"""

config = {
    "MAX_BUFFER_SIZE": 1024,
    "MAX_NUM_CONNECTIONS": 10,
    "SERVER_HOST": "0.0.0.0", # Address the server binds to
    "SERVER_PORT": 5002,
    "REPLICA1_PORT": 5003,
    "REPLICA2_PORT": 5004,
    "SERVER_ADDRESS": "localhost" # The IP address of the server
}
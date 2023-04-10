"""
Basic implementation for configuration values shared across client and server.
"""

config = {
    "MAX_BUFFER_SIZE": 1024,
    "MAX_NUM_CONNECTIONS": 10,
    "SERVER_HOST": "65.112.8.26", # Address the server binds to
    "REPLICA1_HOST": "65.112.8.26", 
    "REPLICA2_HOST": "65.112.8.20",
    "SERVER_PORT": 5002,
    "REPLICA1_PORT": 5003,
    "REPLICA2_PORT": 5004,
    "SERVER_ADDRESS": "localhost" # The IP address of the server
}
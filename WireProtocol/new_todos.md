### Big Questions

1) Figure out how to handle both server and client disconnecting from socket. Right now this isn't working properly so it's hard to test message queue functionality.
2) Figure out if we need to handle potential buffer issues since `socket.send()` and `socket.recv()` do not guarantee that the whole message is sent/received. This probably isn't an issue generally since our messages are small, but for example a problem could arise if the server is trying to send a bunch of queued messages to a client. Check this post: https://stackoverflow.com/questions/43552960/check-socket-with-select-before-using-send. 
3) Figure out how much we need to handle race conditions on the server-side. Have not implemented locking yet.
4) Testing on multiple devices. This could surface unforseen problems.

### Tasks

- Migrate code for server-side handling of "DELETE" and "LIST" messages. We will need to modify `ResponseMessage` accordingly. May make sense to create separate subclasses, e.g. `ListResponse`.
- Unit tests for everything. `test_protocol.py` needs to be rewritten for the new `protocol.py` design.
- Create better display options on client side by modifying `_display_message()` in `client.py`.
- Bunch of `TODO` labels in the codebase, address as needed.
- Clean up configuration code for launching client/server code. 
- Quite a few places where we need to handle exceptions, will try to add `TODO` markers.

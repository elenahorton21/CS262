### Design Questions
- Where should we put handling of the messages, i.e. the client should receive confirmation that a message was sent?
- State management?
- Should we use Docker containers? On one hand allows for consistent environment, on the other may have to deal with some additional networking headaches (ports, etc.).
- Thinking about race conditions for our threading. Some possibilities:
  - Send a message to a username that is being deleted.


- Do we need to send a response from client when a non-response message is sent to it, e.g. if server sends MESSAGE to client, client responses that message is received.

- Doesn't seem like we can assume that send() and recv() use the whole buffer: https://stackoverflow.com/questions/67509709/is-recvbufsize-guaranteed-to-receive-all-the-data-if-sended-data-is-smaller-th

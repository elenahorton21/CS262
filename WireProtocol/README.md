# CS 262: Wire Protocols Assignment
## Elena Horton and Jerry Yang

### Protocol Definition

We implement a pretty simple protocol to fulfill the defined functionality for this assignment. The primary structure is to have an initial keyword that defines the type of message, `TYPE|` followed by the specified username if applicable. 

**Remove an account**

`DELETE|username_to_delete`

**List all accounts**

`LIST|wildcard`

Note: if a wildcard is not provided, this will then list all accounts. Otherwise the server processes the wildcard and only lists the applicable accounts.

**Register a new user**

`USERNAME|username`

Note: the protocol requires that the client first registers their username upon connection. The server either recognizes this as a new username or identifies it as a previous account. 


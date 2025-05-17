# JRPC-OO Python Implementation

A Python implementation of the JRPC-OO library for JSON-RPC communication over WebSockets. This library allows easy bidirectional communication between Python applications, with support for exposing class methods over RPC.

## Features

- Expose Python class methods over JSON-RPC
- Bidirectional communication over WebSockets
- Support for both client and server implementations
- Class method discovery and inheritance support
- Simple Promise-like API for asynchronous calls

## Installation

Install directly from the repository:

```bash
pip install -e .
```

Or with development dependencies:

```bash
pip install -e ".[dev]"
```

## Dependencies

- jsonrpclib-pelix: JSON-RPC implementation
- websocket-client: WebSocket client implementation
- websocket-server: WebSocket server implementation

## Basic Usage

### Server Example

```python
from python import JRPCServer

# Create a class with methods to expose
class MyClass:
    def hello(self, name):
        print(f"Hello {name}!")
        return f"Hello {name} from server"
    
    def add(self, a, b):
        return a + b

# Create server on port 9000
server = JRPCServer(9000, ssl=False)  # Set ssl=False for non-secure connection

# Create class instance and add it to the server
my_obj = MyClass()
server.add_class(my_obj)

# Start the server
server_thread = server.start()

# Keep server running
try:
    while True:
        import time
        time.sleep(1)
except KeyboardInterrupt:
    print("Server stopped")
```

### Client Example

```python
from python import JRPCClient
import time

# Create a class with methods to expose to the server
class ClientClass:
    def remote_callback(self, message):
        print(f"Server called me with: {message}")
        return "Response from client"

# Connect to server
client = JRPCClient("ws://localhost:9000")  # Use ws:// for non-secure connection
client.connect()

# Create instance and expose its methods
client_obj = ClientClass()
client.add_class(client_obj)

# Call server methods using call[] syntax (similar to JS implementation)
client.call["MyClass.hello"]("World").then(
    lambda result: print(f"Result: {result}")
).catch(
    lambda err: print(f"Error: {err}")
)

# Keep client running to respond to server calls
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Client stopped")
```

## Class Reference

### ExposeClass

Helps expose Python class methods over RPC by discovering methods and creating appropriate wrappers.

### JRPCCommon

Base class for both client and server implementations. Handles remote connections and method exposure.

### JRPCServer

Server implementation that listens for WebSocket connections and handles incoming RPC requests.

### JRPCClient

Client implementation that connects to a JRPC server and allows bidirectional communication.

## SSL Support

For secure WebSocket connections, you'll need to provide SSL certificates:

```python
# Server with SSL
server = JRPCServer(9000, use_ssl=True)  # Will look for cert/server.crt and cert/server.key

# Client with SSL
client = JRPCClient("wss://localhost:9000")  # Note the wss:// protocol
```

## Testing

Example clients and server implementations are provided in the `python/tests` directory.

To run the server test:

```bash
python python/tests/server_test.py
```

In separate terminals, run the client tests:

```bash
python python/tests/client1.py
python python/tests/client2.py
```

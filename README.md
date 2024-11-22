# jrpc-oo

Expose objects over the network using the JSON-RPC 2.0 protocol. This repository provides implementations in Node.js, LitElement (Web Components), and Python, allowing seamless RPC communication between different platforms.

## Features

- JSON-RPC 2.0 protocol implementation
- WebSocket-based communication
- Bidirectional RPC calls:
  - Server can call client methods
  - Client can call server methods
  - Enables true peer-to-peer communication
- Multiple language support:
  - Node.js server and client
  - LitElement web components for browser integration
  - Python server and client
- Automatic function exposure and remote execution
- Secure WebSocket support (WSS)
- Bidirectional communication

## Implementations

### Node.js
- Server implementation in `JRPCServer.js`
- Client implementation in `JRPCNodeClient.js`
- Support for automatic class method exposure
- WebSocket-based communication

### LitElement (Web Components)
- Browser-based client implementation in `jrpc-client.js`
- Material Design components integration
- Automatic UI generation for exposed methods
- WebSocket client capabilities

### Python
- Server implementation in `python/jrpc_server.py`
- Client implementation in `python/jrpc_client.py`
- Compatible with Node.js and browser clients
- Async/await support using websockets

## RPC Calling Pattern

All implementations (Node.js, Python, and Browser) use the same consistent pattern for making RPC calls:

```javascript
// Standard RPC calling pattern
jrpcObject['ClassName.methodName'](arg1, arg2, ...)

// Examples:
// JavaScript/Browser
client['Calculator.add'](2, 3)
  .then(result => console.log(result))
  .catch(error => console.error(error));

// Python (with async/await)
result = await client['Calculator.add'](2, 3)

// Node.js
client['TestClass.fn2'](arg1, arg2)
  .then(result => console.log(result))
  .catch(error => console.error(error));
```

This consistent pattern ensures that RPC calls work the same way across all implementations, making it easier to:
- Switch between different implementations
- Write cross-platform code
- Understand and maintain the codebase

## Example Usage

### Node.js Server Example
```javascript
JRPCServer = require('./JRPCServer');

class TestClass {
  fn2(arg1, arg2){
    console.log('fn2');
    console.log('arg1 :', JSON.stringify(arg1, null, 2));
    console.log('arg2 :', JSON.stringify(arg2, null, 2));
    return arg1;
  }
}

let tc = new TestClass;
var JrpcServer = new JRPCServer.JRPCServer(9000); // start a server on port 9000
JrpcServer.addClass(tc); // setup the class for remote use
```

### Browser Client Example (LitElement)
```javascript
import {JRPCClient} from '../jrpc-client.js';
import '@material/mwc-button';

export class LocalJRPC extends JRPCClient {
  firstUpdated() {
    this.serverURI = "wss://0.0.0.0:9000";
  }

  setupDone() {
    let btn = document.createElement('mwc-button');
    btn.raised = true;
    btn.onclick = this.testArgPass;
    btn.textContent = 'TestClass.fn2 arg test';
    this.shadowRoot.appendChild(btn);
  }

  testArgPass() {
    this.call['TestClass.fn2'](1, {0: 'test', 1: [1, 2]})
      .then((result) => console.log(result))
      .catch((e) => console.error(e.message));
  }
}

window.customElements.define('local-jrpc', LocalJRPC);
```

### Python Example
```python
# Server
from python.jrpc_server import JRPCServer

class Calculator:
    def add(self, a, b):
        return {"result": a + b}

server = JRPCServer(host='localhost', port=8080)
server.add_instance(Calculator())
server.start()

# Client
from python.jrpc_client import JRPCClient

client = JRPCClient('ws://localhost:8080')
result = await client.call('Calculator.add', 1, 2)
print(result)  # {"result": 3}
```

## Getting Started

1. Install dependencies:
   ```bash
   npm install  # For Node.js/Browser
   pip install -r python/requirements.txt  # For Python
   ```

2. Start the server:
   ```bash
   # Node.js server
   ./JRPCServerTest.js
   
   # OR Python server
   python python/server.py
   ```

3. For web application demo:
   ```bash
   npm start
   ```
   Then:
   - Clear cert issues: visit https://0.0.0.0:9000
   - Access demo: https://0.0.0.0:8081

## Integration

- See the jrpc-lit-node repo for Node.js/LitElement integration examples
- Python implementation can be integrated directly into any async Python application

## Security

- Uses WSS (WebSocket Secure) for encrypted communication
- Certificate generation scripts included in repository
- Proper error handling and input validation

## License

See LICENSE file for details.

# run the webapp demo :

First install the requirements :
```
npm install
```

## setup the nodejs side

```
./JRPCServerTest.js
```

## setup the webapp

To setup run the webapp (answer defaults to the key generation question) :
```
npm start
```
Now clear cert issues in the browser go to the following url to clear the websocket port 9000 : https://0.0.0.0:9000

Now finally run the demo in the webapp : https://0.0.0.0:8081

## in the webapp

You will see the class TestClass functions exposed as buttons. Press some buttons and look at the nodejs side/browser console to see function executions and returned arguments.

## integrate into your apps

Have a look at the jrpc-lit-node repo for an example of integration.

# run the nodejs demo :

First install the requirements :
```
npm install
```
## run the server
```
./JRPCServerTest.js
```
## run the clients in parallel and test

```
./tests/multiTest.sh

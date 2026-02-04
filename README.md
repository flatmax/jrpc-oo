# jrpc-oo

Expose objects over the network using JSON-RPC 2.0 over WebSockets. Implementations for Node.js, LitElement (browser), and Python enable seamless cross-platform RPC communication.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [RPC Calling Pattern](#rpc-calling-pattern)
- [Node.js](#nodejs)
  - [Server](#nodejs-server)
  - [Client](#nodejs-client)
- [Browser (LitElement)](#browser-litelement)
- [Python](#python)
  - [Server](#python-server)
  - [Client](#python-client)
- [Bidirectional Communication](#bidirectional-communication)
- [Running the Demos](#running-the-demos)
- [Security (WSS)](#security-wss)
- [License](#license)

## Features

- **JSON-RPC 2.0** protocol over WebSockets
- **Bidirectional RPC**: Server can call client methods and vice versa
- **Cross-platform**: Node.js, Browser (LitElement), and Python implementations
- **Automatic method exposure**: Simply add a class and all its methods become callable
- **Multiple client support**: Server can manage many connected clients
- **Secure WebSocket (WSS)** support with certificate generation

## Installation

### Node.js / Browser

```bash
npm install
```

### Python

```bash
pip install -e .
# Or install dependencies directly:
pip install websockets asyncio
```

## Quick Start

### 1. Start a Server (Node.js)

```bash
./JRPCServerTest.js
```

### 2. Connect a Client (Browser)

```bash
npm start
# Visit https://0.0.0.0:8081
```

### 3. Or Connect a Python Client

```bash
python jrpc_oo/tests/JRPCClientTest.py ws://0.0.0.0:9000
```

## RPC Calling Pattern

All implementations use the same consistent pattern:

```
object['ClassName.methodName'](arg1, arg2, ...)
```

| Platform | Syntax |
|----------|--------|
| JavaScript | `this.server['TestClass.fn2'](arg1, arg2).then(result => ...)` |
| Python | `result = await self.server['TestClass.fn2'](arg1, arg2)` |

Call all connected remotes:

| Platform | Syntax |
|----------|--------|
| JavaScript | `this.call['ClassName.method'](args).then(results => ...)` |
| Python | `results = await self.call['ClassName.method'](args)` |

Results from `call` return a dictionary: `{uuid: result, ...}` for each connected remote.

## Node.js

### Node.js Server

```javascript
const JRPCServer = require('./JRPCServer');

class Calculator {
  add(a, b) {
    return a + b;
  }
  
  multiply(a, b) {
    return a * b;
  }
}

const calc = new Calculator();
const server = new JRPCServer.JRPCServer(9000, 60, false); // port, timeout, ssl
server.addClass(calc);

console.log('Server running on ws://0.0.0.0:9000');
```

### Node.js Client

```javascript
const JRPCNodeClient = require('./JRPCNodeClient').JRPCNodeClient;

class ClientMethods {
  // Methods here can be called by the server
  notify(message) {
    console.log('Server says:', message);
    return 'received';
  }
}

const client = new JRPCNodeClient('ws://0.0.0.0:9000');
client.addClass(new ClientMethods());

// Once connected, call server methods:
// client.server['Calculator.add'](2, 3).then(result => console.log(result));
```

## Browser (LitElement)

```javascript
import { JRPCClient } from './jrpc-client.js';

class MyApp extends JRPCClient {
  constructor() {
    super();
    this.remoteTimeout = 60;
  }

  // Called when connection is ready
  setupDone() {
    // Now you can call server methods
    this.testCalculator();
  }

  async testCalculator() {
    try {
      const sum = await this.server['Calculator.add'](5, 3);
      console.log('5 + 3 =', sum);
      
      const product = await this.server['Calculator.multiply'](4, 7);
      console.log('4 * 7 =', product);
    } catch (e) {
      console.error('RPC error:', e);
    }
  }

  // This method can be called BY the server
  showAlert(message) {
    alert(message);
    return 'alert shown';
  }
}

customElements.define('my-app', MyApp);
```

```html
<my-app serverURI="ws://0.0.0.0:9000"></my-app>
```

## Python

### Python Server

```python
import asyncio
from jrpc_oo import JRPCServer

class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b

async def main():
    server = JRPCServer(port=9000)
    server.add_class(Calculator())
    
    await server.start()
    print('Server running on ws://0.0.0.0:9000')
    
    # Keep running
    await asyncio.Future()

asyncio.run(main())
```

### Python Client

```python
import asyncio
from jrpc_oo import JRPCClient

class ClientMethods:
    """Methods the server can call on this client."""
    def notify(self, message):
        print(f'Server says: {message}')
        return 'received'

async def main():
    client = JRPCClient('ws://0.0.0.0:9000')
    client.add_class(ClientMethods())
    
    # Connect and wait for setup
    connect_task = asyncio.create_task(client.connect())
    
    # Wait for connection
    await asyncio.sleep(2)
    
    if client.connected:
        # Call server methods
        result = await client.server['Calculator.add'](10, 20)
        print(f'10 + 20 = {result}')
        
        result = await client.server['Calculator.multiply'](6, 7)
        print(f'6 * 7 = {result}')
    
    await connect_task

asyncio.run(main())
```

## Bidirectional Communication

The server can call methods on connected clients:

### Server Side (Node.js)

```javascript
class ServerClass {
  constructor() {
    // get_server() is added when class is registered
  }
  
  async triggerClientAlert() {
    // Call method on connected client
    const result = await this.getServer()['ClientMethods.showAlert']('Hello from server!');
    console.log('Client responded:', result);
  }
}
```

### Server Side (Python)

```python
class ServerClass:
    async def trigger_client_alert(self):
        # Call method on connected client
        result = await self.get_server()['ClientMethods.show_alert']('Hello from server!')
        print(f'Client responded: {result}')
```

## Running the Demos

### Node.js Server + Browser Client

```bash
# Terminal 1: Start the server
./JRPCServerTest.js

# Terminal 2: Start the web server
npm start

# Browser: Visit https://0.0.0.0:8081
# (First visit https://0.0.0.0:9000 to accept the self-signed certificate)
```

### Node.js Server + Multiple Node.js Clients

```bash
./tests/multiTest.sh
```

### Python Server + Browser Client

```bash
# Terminal 1: Start Python server
python jrpc_oo/tests/JRPCServerTest.py no_wss

# Terminal 2: Start web server
npm run start:no_wss

# Browser: Visit http://0.0.0.0:8081
```

### Python Server + Python Client

```bash
# Terminal 1: Start server
python jrpc_oo/tests/JRPCServerTest.py no_wss

# Terminal 2: Connect client
python jrpc_oo/tests/JRPCClientTest.py ws://0.0.0.0:9000
```

## Security (WSS)

For secure WebSocket connections, certificates are auto-generated on first run:

```bash
# Node.js with WSS (default)
./JRPCServerTest.js

# Node.js without WSS
./JRPCServerTest.js no_wss

# Python with WSS (uses mkcert)
python jrpc_oo/tests/JRPCServerTest.py

# Python without WSS
python jrpc_oo/tests/JRPCServerTest.py no_wss
```

When using WSS with self-signed certificates, visit `https://0.0.0.0:9000` in your browser first to accept the certificate.

## License

BSD-3-Clause. See [LICENSE](LICENSE) for details.

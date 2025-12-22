# AI Instructions for JRPC-OO

JRPC-OO exposes objects over WebSockets using JSON-RPC 2.0. Implementations: Node.js, LitElement (browser), Python (asyncio).

## Core Files

| Component | JavaScript | Python |
|-----------|------------|--------|
| Common | `JRPCCommon.js` | `jrpc_oo/JRPCCommon.py` |
| Server | `JRPCServer.js` | `jrpc_oo/JRPCServer.py` |
| Client | `JRPCNodeClient.js` / `jrpc-client.js` | `jrpc_oo/JRPCClient.py` |

## Async Nature of RPC Calls

**All RPC calls are asynchronous.** The WebSocket communication is inherently async, so:

- **JavaScript:** All RPC calls return `Promise` objects. Use `.then()/.catch()` or `async/await`.
- **Python:** All RPC calls are coroutines. Use `await` to get results.

**Exposed methods (methods you add via `addClass`/`add_class`):**
- **JavaScript:** Can be sync or async (Promises are automatically resolved)
- **Python:** Must be synchronous functions. The framework wraps them internally. If you need async behavior, schedule tasks with `asyncio.create_task()` inside your method.

## Lifecycle Methods

**JavaScript:**
- `setupDone()` - System ready for RPC calls
- `remoteIsUp()` - Remote connected but not ready
- `remoteDisconnected(uuid)` - Remote disconnected

**Python (asyncio):**
- `setup_done()` - System ready
- `remote_is_up()` - Remote connected
- `remote_disconnected(uuid)` - Remote disconnected

## Adding Classes

```javascript
// JS - typically in connectedCallback or remoteIsUp
this.addClass(instance, 'OptionalName');
```

```python
# Python
server.add_class(instance, "OptionalName")
```

Once added, class gains: `getRemotes()`/`get_remotes()`, `getCall()`/`get_call()`, `getServer()`/`get_server()` (legacy)

## Making RPC Calls

**All calls are async - JavaScript uses Promises, Python uses async/await.**

```javascript
// JS - call all remotes (returns Promise<{uuid: result, ...}>)
this.call['ClassName.methodName'](arg1, arg2)
  .then(result => { /* result is {uuid: value, ...} */ })
  .catch(err => { /* handle error */ });

// JS with async/await
const result = await this.call['ClassName.methodName'](arg1, arg2);

// JS - single remote (returns Promise<result>)
this.remotes[uuid].rpcs['ClassName.methodName'](args)
  .then(result => {});

// JS - legacy (single remote only, returns Promise)
this.server['ClassName.methodName'](args).then(result => {});
```

```python
# Python - call all remotes (returns dict {uuid: result, ...})
result = await self.get_call()['ClassName.methodName'](arg1, arg2)

# Python - single remote
result = await self.remotes[uuid].rpcs['ClassName.methodName'](args)

# Python - legacy (single remote only)
result = await self.server['ClassName.methodName'](args)
```

## Connection Lifecycle (Async)

**JavaScript (browser/Node.js):**
```javascript
// Browser - connection happens automatically when serverURI is set
client.serverURI = 'wss://localhost:9000';

// Node.js client
const client = new JRPCNodeClient('wss://localhost:9000');
// Connection is initiated in constructor, setupDone() called when ready
```

**Python:**
```python
# Server (async)
server = JRPCServer(port=9000)
await server.start()  # Starts listening

# Client (async)
client = JRPCClient('ws://localhost:9000')
await client.connect()  # Blocks while connected, handles messages
```

## File Organization

- `customElements.define` calls go in `webapp/` directory
- Class implementations go in `webapp/src/` directory
- Tests in `tests/` (JS) and `jrpc_oo/tests/` (Python)

## LitElement Lifecycle

Key methods: `constructor()`, `connectedCallback()`, `disconnectedCallback()`, `render()`, `firstUpdated()`, `updated()`, `updateComplete` (Promise)

## SSL/WSS

**JS:** Certs in `./cert/server.crt`, `./cert/server.key`
```javascript
new JRPCServer.JRPCServer(9000, 60, true);  // SSL
new JRPCServer.JRPCServer(9000, 60, false); // No SSL
```

**Python:** Uses `mkcert` via `jrpc_oo/cert.py`

## Running Tests

```bash
# JS server + browser
./JRPCServerTest.sh [no_wss]

# Python server
python jrpc_oo/tests/JRPCServerTest.py [no_wss]

# Python client
python jrpc_oo/tests/JRPCClientTest.py ws://0.0.0.0:9000
```

## Error Handling

```javascript
// JS
this.call['Class.method'](args)
  .then(result => { /* success */ })
  .catch(err => { /* handle error */ });
```

```python
# Python
from jrpc_oo.JRPCCommon import RPCMethodNotFoundError
try:
    result = await self.get_call()['Class.method'](args)
except RPCMethodNotFoundError as e:
    print(f'Method not found: {e.method_name}')
except Exception as e:
    print(f'RPC error: {e}')
```

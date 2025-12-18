# AI Instructions for JRPC-OO

JRPC-OO exposes objects over WebSockets using JSON-RPC 2.0. Implementations: Node.js, LitElement (browser), Python (asyncio).

## Core Files

| Component | JavaScript | Python |
|-----------|------------|--------|
| Common | `JRPCCommon.js` | `jrpc_oo/JRPCCommon.py` |
| Server | `JRPCServer.js` | `jrpc_oo/JRPCServer.py` |
| Client | `JRPCNodeClient.js` / `jrpc-client.js` | `jrpc_oo/JRPCClient.py` |

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

```javascript
// JS - call all remotes (returns {uuid: result, ...})
this.call['ClassName.methodName'](arg1, arg2).then(result => {});

// JS - single remote
this.remotes[uuid].rpcs['ClassName.methodName'](args).then(result => {});

// JS - legacy (single remote only)
this.server['ClassName.methodName'](args).then(result => {});
```

```python
# Python - call all remotes
result = await self.get_call()['ClassName.methodName'](arg1, arg2)

# Python - legacy
result = await self.server['ClassName.methodName'](args)
```

**Important:** Python exposed methods must be synchronous (can schedule async tasks internally).

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

```python
from jrpc_oo.JRPCCommon import RPCMethodNotFoundError
try:
    result = await self.get_call()['Class.method'](args)
except RPCMethodNotFoundError as e:
    print(f'Method not found: {e.method_name}')
```

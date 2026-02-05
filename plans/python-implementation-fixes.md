# Python JRPC Implementation Fixes Plan

## Overview

This plan addresses issues found during the audit of the Python JRPC implementation compared to the JavaScript reference implementation.

## Critical Issues (Phase 1)

### 1.1 JRPC2.py - Response Parsing Logic Bug (FIXED - verify only)

**Status:** The code at line 89 already has correct parentheses:
```python
if 'id' in message and 'result' in message or 'error' in message:
```
This still needs fixing - the current code is buggy.

**File:** `jrpc_oo/JRPC2.py`
**Line:** ~89
**Severity:** HIGH

**Problem:**
```python
if 'id' in message and 'result' in message or 'error' in message:
```
Operator precedence causes this to be evaluated as:
```python
('id' in message and 'result' in message) or 'error' in message
```
Any message with just `'error'` key is incorrectly treated as a response.

**Fix:**
```python
if 'id' in message and ('result' in message or 'error' in message):
```

**Test:** Send a malformed message with only `{'error': 'test'}` - should not be processed as a response.

---

### 1.2 JRPCServer.py - `self.server` Attribute Collision

**File:** `jrpc_oo/JRPCServer.py`
**Line:** 21
**Severity:** HIGH

**Problem:**
Parent `JRPCCommon.__init__()` sets `self.server = {}` for RPC method storage.
Child `JRPCServer.__init__()` overwrites it with `self.server = None` (websocket server reference).
This breaks the legacy `server` functionality for calling remote methods.

**Fix:**
Rename websocket server attribute to `self.ws_server`:
```python
self.ws_server = None  # WebSocket server instance
self.clients = {}
```

Update all references in `JRPCServer.py`:
- `start()`: `self.ws_server = await websockets.serve(...)`
- `stop()`: `if self.ws_server:`

---

### 1.3 JRPCCommon.py - Missing `await` in setup_remote

**File:** `jrpc_oo/JRPCCommon.py`
**Line:** ~137
**Severity:** HIGH

**Problem:**
```python
remote.call('system.listComponents', [], lambda err, result: 
    asyncio.create_task(self._handle_list_components_async(err, result, remote)))
```
The `remote.call()` method uses `asyncio.create_task(self._transmit_message(...))` internally, but `setup_remote` is not async. This works but creates a timing issue - if the connection is slow, `setup_done()` might never be called because the task isn't awaited.

More critically, if `setup_remote` is called from a context without a running event loop, `asyncio.create_task()` will fail.

**Fix:**
Make `setup_remote` async or ensure it's always called from an async context. The JS version handles this implicitly via callbacks.

---

## Medium Issues (Phase 2)

### 2.1 JRPCCommon.py - Deprecated `get_event_loop()`

**File:** `jrpc_oo/JRPCCommon.py`
**Line:** 193
**Severity:** MEDIUM

**Problem:**
`asyncio.get_event_loop()` is deprecated in Python 3.10+.

**Fix:**
```python
future = asyncio.get_running_loop().create_future()
```

---

### 2.2 JRPC2.py - Responses Sent for Notifications

**File:** `jrpc_oo/JRPC2.py`
**Line:** ~119
**Severity:** MEDIUM

**Problem:**
JSON-RPC 2.0 notifications (requests without `id`) should not receive responses.
Currently `_send_response` is called even when `request_id` is None.

**Fix:**
Add early return in request handling when `id` is missing:
```python
if 'method' in message:
    method = message.get('method')
    params = message.get('params', {})
    request_id = message.get('id')  # May be None for notifications
    
    if method in self.methods:
        try:
            def response_callback(err, res):
                if request_id is not None:  # Only respond if not a notification
                    self._send_response(request_id, err, res)
            
            self.methods[method](params, response_callback)
        except Exception as e:
            if request_id is not None:
                self._send_error(request_id, str(e))
```

---

## Low Issues (Phase 3)

### 3.1 JRPCCommon.py - Dead Code in Server Attribute Check

**File:** `jrpc_oo/JRPCCommon.py`
**Lines:** 38-42
**Severity:** LOW

**Problem:**
```python
self.server = {}   # Set first

# Check comes AFTER assignment - always false
if hasattr(self, 'server') and not isinstance(self.server, dict):
    self._original_server = self.server
    self.server = {}
```

**Fix:**
Remove dead code or reorder:
```python
# Check BEFORE assignment if needed
if hasattr(self, 'server') and not isinstance(self.server, dict):
    self._original_server = self.server
self.server = {}
```

Or simply remove the check entirely since the class controls initialization.

---

### 3.2 JRPC2.py - Missing Request Timeout Handling

**File:** `jrpc_oo/JRPC2.py`
**Line:** `__init__` and `call` methods
**Severity:** LOW

**Problem:**
The `remote_timeout` parameter is stored but never used. Pending requests in `self.requests` are never cleaned up if the remote doesn't respond, causing memory leaks and hanging callbacks.

The JavaScript implementation uses `jrpc` library which handles timeouts internally.

**Fix:**
Add timeout handling in the `call` method:
```python
def call(self, method: str, params: Any, callback: Callable):
    request_id = str(uuid.uuid4())
    # ... existing code ...
    
    # Schedule timeout cleanup
    async def timeout_handler():
        await asyncio.sleep(self.remote_timeout)
        if request_id in self.requests:
            cb = self.requests.pop(request_id)
            cb(Exception(f"Request timeout after {self.remote_timeout}s"), None)
    
    asyncio.create_task(timeout_handler())
```

---

### 3.3 JRPCClient.py - Missing Reconnection Logic

**File:** `jrpc_oo/JRPCClient.py`
**Severity:** LOW

**Problem:**
When the connection drops, there's no automatic reconnection. The JavaScript browser client allows setting `serverURI` again to reconnect, but the Python client has no equivalent mechanism.

**Fix:**
Add a `reconnect()` method or allow `connect()` to be called multiple times:
```python
async def reconnect(self, delay: float = 1.0):
    """Attempt to reconnect after a delay."""
    await asyncio.sleep(delay)
    await self.connect()
```

---

### 3.4 ExposeClass.py - Async Method Support

**File:** `jrpc_oo/ExposeClass.py`
**Line:** ~50-65 (wrapper function)
**Severity:** LOW

**Problem:**
The wrapper in `expose_all_fns` doesn't properly handle async methods. If an exposed method is `async def`, calling it returns a coroutine that's never awaited.

**Fix:**
```python
def wrapper(params, next_cb, method_name=method_name):
    """Wrapper function for the method call."""
    try:
        method = getattr(cls_instance, method_name)
        
        # Handle args format used by JS implementation
        if isinstance(params, dict) and 'args' in params:
            args = params['args']
            if isinstance(args, list):
                result = method(*args)
            else:
                result = method(args)
        else:
            result = method(params)
        
        # Handle async methods
        if asyncio.iscoroutine(result):
            async def await_and_callback():
                try:
                    actual_result = await result
                    return next_cb(None, actual_result)
                except Exception as e:
                    return next_cb(str(e), None)
            asyncio.create_task(await_and_callback())
            return  # Don't call next_cb here
            
        return next_cb(None, result)
    except Exception as e:
        print(f"Failed: {e}")
        return next_cb(str(e), None)
```

---

### 3.5 JRPCCommon.py - Race Condition in setup_fns

**File:** `jrpc_oo/JRPCCommon.py`
**Line:** ~170-230
**Severity:** LOW

**Problem:**
When multiple remotes connect simultaneously, there's a race condition where `self.call[fn_name]` might be partially set up when another remote triggers `setup_fns`.

**Fix:**
Use a lock or atomic updates:
```python
def __init__(self):
    # ... existing code ...
    self._setup_lock = asyncio.Lock()

async def setup_fns_safe(self, fn_names, remote):
    async with self._setup_lock:
        self.setup_fns(fn_names, remote)
```

---

### 3.6 JRPCServer.py - Unused `clients` Dictionary

**File:** `jrpc_oo/JRPCServer.py`
**Line:** 22
**Severity:** LOW

**Problem:**
```python
self.clients = {}
```
This dictionary is initialized but never populated or used. The parent class `JRPCCommon` already tracks remotes via `self.remotes`.

**Fix:**
Remove the unused `self.clients = {}` line, or if client tracking by websocket is needed, implement it properly.

---

### 3.7 JRPCClient.py - Blocking `connect()` Design

**File:** `jrpc_oo/JRPCClient.py`
**Line:** ~30-50
**Severity:** LOW

**Problem:**
The `connect()` method enters `async for message in self.ws:` which blocks until the connection closes. This means:
1. Code after `await client.connect()` only runs after disconnect
2. The caller can't do anything else with the client

The JS version uses event handlers (`ws.on('message', ...)`) which don't block.

**Fix:**
Split into connect + message loop, or spawn the message loop as a background task:
```python
async def connect(self):
    """Connect to the WebSocket server."""
    self.ws = await websockets.connect(self.server_uri)
    self.connected = True
    remote = self.create_remote(self.ws)
    
    # Spawn message handler as background task
    self._message_task = asyncio.create_task(self._message_loop(remote))

async def _message_loop(self, remote):
    """Handle incoming messages in background."""
    try:
        async for message in self.ws:
            if isinstance(message, bytes):
                message = message.decode('utf-8')
            remote.receive(message)
    except websockets.exceptions.ConnectionClosed:
        self.connected = False
```

---

### 3.8 JRPCCommon.py - IS_BROWSER Check Never True

**File:** `jrpc_oo/JRPCCommon.py`
**Lines:** 14-18
**Severity:** LOW

**Problem:**
```python
try:
    import websockets
    IS_BROWSER = False
except ImportError:
    IS_BROWSER = True
```
This check is vestigial from the JS implementation. In Python, `websockets` will always be available (it's a dependency), and Python code never runs "in browser" in the same way JS does. The `IS_BROWSER` variable is defined but never used anywhere.

**Fix:**
Remove the dead code:
```python
import websockets

# Remove IS_BROWSER entirely - Python doesn't run in browsers
```

---

### 3.9 ExposeClass.py - `inspect.isfunction` vs `inspect.ismethod`

**File:** `jrpc_oo/ExposeClass.py`
**Line:** 36
**Severity:** LOW

**Problem:**
```python
methods = [
    f"{class_name}.{name}" 
    for name, method in inspect.getmembers(c, predicate=inspect.isfunction)
    if not name.startswith('_')
]
```
Using `inspect.isfunction` on a class object works, but it's fragile. When iterating `cls.__mro__`, we get class objects not instances, so `isfunction` is correct. However, this misses methods decorated with `@staticmethod` or `@classmethod`.

The JS version uses `Object.getOwnPropertyNames(p)` which gets all properties regardless of type, then filters by checking they're not constructor and don't start with `__`.

**Fix:**
For full parity with JS, consider:
```python
methods = [
    f"{class_name}.{name}"
    for name in dir(c)
    if not name.startswith('_') 
    and callable(getattr(c, name, None))
    and name in c.__dict__  # Only methods defined on this class, not inherited
]
```
Or keep current behavior but document that `@staticmethod`/`@classmethod` aren't exposed.

---

## Test Plan

### Unit Tests

Create `jrpc_oo/tests/test_unit.py`:

```python
"""
Unit tests for JRPC Python implementation.
"""
import pytest
import asyncio
import json

# Test categories:
# 1. JRPC2 protocol tests
# 2. ExposeClass tests  
# 3. JRPCCommon tests
# 4. Integration tests
```

#### Test Cases for JRPC2

| Test ID | Description | Input | Expected |
|---------|-------------|-------|----------|
| T1.1 | Valid response parsing | `{'id': '1', 'result': 'ok'}` | Callback invoked with result |
| T1.2 | Valid error response | `{'id': '1', 'error': {...}}` | Callback invoked with error |
| T1.3 | Malformed message (error only) | `{'error': 'test'}` | Ignored, no callback |
| T1.4 | Notification (no id) | `{'method': 'test', 'params': {}}` | Method called, no response sent |
| T1.5 | Request with id | `{'id': '1', 'method': 'test'}` | Method called, response sent |
| T1.6 | Method not found | `{'id': '1', 'method': 'unknown'}` | Error response sent |

#### Test Cases for ExposeClass

| Test ID | Description | Input | Expected |
|---------|-------------|-------|----------|
| T2.1 | Get all functions | Class with 3 methods | List of 3 `ClassName.method` strings |
| T2.2 | Inheritance | Child class | Parent methods included |
| T2.3 | Exclude private | Class with `_private` | Not in list |
| T2.4 | Args unpacking | `{'args': [1, 2]}` | Method called with `(1, 2)` |
| T2.5 | Empty args | `{'args': []}` | Method called with no args |

#### Test Cases for JRPCCommon

| Test ID | Description | Input | Expected |
|---------|-------------|-------|----------|
| T3.1 | New remote creation | - | Remote added to `self.remotes` |
| T3.2 | Remote removal | UUID | Remote removed, `call` updated |
| T3.3 | Setup functions | `['Class.method']` | `self.call['Class.method']` exists |
| T3.4 | Multiple remotes same fn | Two remotes | `call[fn]` calls both |

### Integration Tests

Create `jrpc_oo/tests/test_integration.py`:

| Test ID | Description | Setup | Expected |
|---------|-------------|-------|----------|
| T4.1 | Server-client connect | Start server, connect client | `system.listComponents` exchanged |
| T4.2 | Client calls server | Client calls exposed method | Result returned |
| T4.3 | Server calls client | Server calls client method | Result returned |
| T4.4 | Multiple clients | 2 clients connect | `call[fn]` reaches both |
| T4.5 | Client disconnect | Client disconnects | Removed from `remotes` |
| T4.6 | Concurrent calls | 10 simultaneous calls | All return correctly |

### Cross-Language Tests

Create `jrpc_oo/tests/test_interop.py`:

| Test ID | Description | Setup | Expected |
|---------|-------------|-------|----------|
| T5.1 | Python client → JS server | Run JRPCServerTest.js | Client can call methods |
| T5.2 | JS client → Python server | Run JRPCServerTest.py | Client can call methods |
| T5.3 | Mixed clients | Py server, JS+Py clients | Both receive broadcasts |

---

## Implementation Order

### Phase 1: Critical Fixes (Day 1) ✅ COMPLETE
1. [x] Fix JRPC2.py response parsing (Issue 1.1)
2. [x] Fix JRPCServer.py attribute collision (Issue 1.2)
3. [x] Create basic unit tests for fixes (14 tests passing)

### Phase 2: Medium Fixes (Day 2) ✅ COMPLETE
4. [x] Fix deprecated get_event_loop (Issue 2.1)
5. [x] Fix notification response handling (Issue 2.2)
6. [x] Add unit tests for JRPC2 protocol
7. [x] Fix deprecated asyncio.iscoroutinefunction (use inspect.iscoroutinefunction)

### Phase 3: Cleanup & Tests (Day 3) ✅ COMPLETE
8. [x] Remove dead code (Issue 3.1)
9. [x] Add request timeout handling (Issue 3.2)
10. [x] Add async method support in ExposeClass (Issue 3.4)
11. [x] Add unit tests for new functionality (24 tests passing)

### Phase 4: Interop Testing (Day 4) ✅ COMPLETE
12. [x] Create Python integration tests (Python server + Python client) - 13 tests passing
13. [x] Create cross-language test harness (run_interop_tests.sh)
14. [x] Test: Python client → JS server - PASSED
15. [x] Test: JS client → Python server - PASSED
16. [x] Test: Mixed clients (JS + Python) → Python server - PASSED
17. [x] Document any behavioral differences (see notes below)
18. [x] Test: JS server → Python client (bidirectional) - PASSED

All 4 cross-language interop tests passing (both directions for both server types).

### Phase 5: Enhancements (Future)
18. [ ] Add reconnection logic to JRPCClient (Issue 3.3)
19. [ ] Add thread-safety for concurrent connections (Issue 3.5)
20. [ ] Consider deprecation path for `self.server` (matches JS "legacy" comments)

---

## Test File Structure

```
jrpc_oo/
├── tests/
│   ├── __init__.py
│   ├── test_unit.py          # Unit tests for each class
│   ├── test_integration.py   # Python-only integration tests
│   ├── test_interop.py       # Cross-language tests
│   ├── conftest.py           # Pytest fixtures
│   ├── Client1.py            # (existing)
│   ├── Client2.py            # (existing)
│   └── ...
```

### Pytest Configuration

Add to `pyproject.toml`:
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["jrpc_oo/tests"]
python_files = ["test_*.py"]
```

### Dependencies to Add

```toml
[project.optional-dependencies]
test = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
    "pytest-timeout>=2.0",
]
```

---

## Success Criteria

1. All unit tests pass
2. Integration tests pass
3. Cross-language tests pass:
   - Python client can connect to JS server (JRPCServerTest.js)
   - JS client can connect to Python server (JRPCServerTest.py)
4. No regressions in existing test files (Client1.py, Client2.py, etc.)

---

## Notes

- The `self.server` dict is marked as "legacy" in JS comments - consider deprecation path
- Python uses `async/await` throughout; ensure all callers handle this correctly
- The `call[fn]` pattern calls ALL remotes - document this clearly

---

## Additional Observations

### Behavioral Differences from JavaScript

1. **Error Handling:** Python uses exceptions extensively; JS uses callback-style `(err, result)`. The Python implementation wraps this correctly but error propagation paths differ.

2. **Event Loop:** Python requires explicit async context; JS is inherently event-driven. Test files must use `asyncio.run()` or pytest-asyncio.

3. **Method Resolution:** Python's `inspect.getmembers` vs JS prototype chain walking behave slightly differently for properties vs methods.

### Code Quality Improvements (Non-blocking)

1. **Type Hints:** Add comprehensive type hints to all public methods for better IDE support and documentation.

2. **Logging:** Replace `print()` statements with proper `logging` module usage for production readiness.

3. **Docstrings:** Some methods lack docstrings or have incomplete documentation.

4. **Constants:** Magic strings like `"system.listComponents"` should be constants.

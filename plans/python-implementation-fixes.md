# Python JRPC Implementation Fixes Plan

## Overview

This plan addresses issues found during the audit of the Python JRPC implementation compared to the JavaScript reference implementation.

## Critical Issues (Phase 1)

### 1.1 JRPC2.py - Response Parsing Logic Bug

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

### Phase 1: Critical Fixes (Day 1)
1. [ ] Fix JRPC2.py response parsing (Issue 1.1)
2. [ ] Fix JRPCServer.py attribute collision (Issue 1.2)
3. [ ] Create basic unit tests for fixes

### Phase 2: Medium Fixes (Day 2)
4. [ ] Fix deprecated get_event_loop (Issue 2.1)
5. [ ] Fix notification response handling (Issue 2.2)
6. [ ] Add unit tests for JRPC2 protocol

### Phase 3: Cleanup & Tests (Day 3)
7. [ ] Remove dead code (Issue 3.1)
8. [ ] Complete unit test coverage
9. [ ] Add integration tests

### Phase 4: Interop Testing (Day 4)
10. [ ] Create cross-language test harness
11. [ ] Verify JS ↔ Python compatibility
12. [ ] Document any behavioral differences

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

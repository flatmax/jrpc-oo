#!/bin/bash
# Cross-language interoperability tests for JRPC
#
# Test matrix:
#   1. Python client → JS server
#   2. JS client → Python server  
#   3. Mixed clients (JS + Python) → Python server

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=============================================="
echo "JRPC Cross-Language Interoperability Tests"
echo "=============================================="
echo ""

# Check dependencies
if ! command -v node &> /dev/null; then
    echo -e "${RED}ERROR: Node.js is required but not installed${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is required but not installed${NC}"
    exit 1
fi

cd "$ROOT_DIR"

# Track results
TEST1_RESULT=1
TEST2_RESULT=1
TEST3_RESULT=1
TEST4_RESULT=1

# Cleanup function
cleanup() {
    echo "Cleaning up..."
    jobs -p | xargs -r kill 2>/dev/null || true
    wait 2>/dev/null || true
}
trap cleanup EXIT

# ==============================================
echo ""
echo -e "${YELLOW}Test 1: Python Client → JS Server${NC}"
echo "----------------------------------"

echo "Starting JS server (no SSL)..."
node JRPCServerTest.js no_wss &
JS_PID=$!
sleep 3

if ! kill -0 $JS_PID 2>/dev/null; then
    echo -e "${RED}JS server failed to start${NC}"
else
    echo "Running Python client test..."
    if python3 jrpc_oo/tests/test_interop_js_server.py; then
        TEST1_RESULT=0
        echo -e "${GREEN}Test 1: PASSED ✓${NC}"
    else
        echo -e "${RED}Test 1: FAILED ✗${NC}"
    fi
fi

# Kill JS server
kill $JS_PID 2>/dev/null || true
wait $JS_PID 2>/dev/null || true
sleep 1

# ==============================================
echo ""
echo -e "${YELLOW}Test 2: JS Client → Python Server${NC}"
echo "----------------------------------"

echo "Starting Python server..."
python3 jrpc_oo/tests/test_interop_py_server.py --timeout=20 --no-auto-test &
PY_PID=$!
sleep 3

if ! kill -0 $PY_PID 2>/dev/null; then
    echo -e "${RED}Python server failed to start${NC}"
else
    echo "Running JS client with RPC calls..."
    # JS client connects, calls Python server methods, verifies results
    timeout 15 node -e "
const JRPCNodeClient = require('./JRPCNodeClient').JRPCNodeClient;

class TestClass {
  uniqueFn1(i, str) { return i+1; }
  commonFn() { return 'JS Client'; }
}

let jrnc = new JRPCNodeClient('ws://127.0.0.1:9000');
jrnc.addClass(new TestClass());

// Override setupDone to run tests after connection established
const originalSetupDone = jrnc.setupDone.bind(jrnc);
jrnc.setupDone = async function() {
  originalSetupDone();
  console.log('JS client connected, running RPC tests...');
  
  let passed = 0;
  let failed = 0;
  
  try {
    // Test 1: Call fn1
    console.log('Test: Calling TestClass.fn1()...');
    const result1 = await jrnc.server['TestClass.fn1']();
    if (result1 && result1.includes('fn1')) {
      console.log('  ✓ fn1 returned:', result1);
      passed++;
    } else {
      console.log('  ✗ fn1 unexpected result:', result1);
      failed++;
    }
    
    // Test 2: Call fn2 with args
    console.log('Test: Calling TestClass.fn2(42, {key: \"value\"})...');
    const result2 = await jrnc.server['TestClass.fn2'](42, {key: 'value'});
    if (result2 === 42) {
      console.log('  ✓ fn2 returned:', result2);
      passed++;
    } else {
      console.log('  ✗ fn2 unexpected result:', result2, '(expected 42)');
      failed++;
    }
    
    // Test 3: Call fn3
    console.log('Test: Calling TestClass.fn3({test: \"data\"})...');
    const result3 = await jrnc.server['TestClass.fn3']({test: 'data'});
    if (result3 && result3.includes('fn3')) {
      console.log('  ✓ fn3 returned:', result3);
      passed++;
    } else {
      console.log('  ✗ fn3 unexpected result:', result3);
      failed++;
    }
    
    console.log('----------------------------------------');
    console.log('JS→Python RPC tests:', passed, 'passed,', failed, 'failed');
    
    if (failed === 0) {
      console.log('TEST2_SUCCESS');
    }
    
  } catch (err) {
    console.log('  ✗ Error:', err.message);
    failed++;
  }
  
  // Exit after tests
  setTimeout(() => process.exit(failed > 0 ? 1 : 0), 1000);
};
" 2>&1 | tee /tmp/test2_output.txt &
    CLIENT_PID=$!
    
    # Wait for client to complete tests
    wait $CLIENT_PID 2>/dev/null
    CLIENT_EXIT=$?
    
    # Check if tests passed
    if grep -q "TEST2_SUCCESS" /tmp/test2_output.txt 2>/dev/null; then
        TEST2_RESULT=0
        echo -e "${GREEN}Test 2: JS client called Python server methods ✓${NC}"
    else
        echo -e "${RED}Test 2: JS client RPC calls failed${NC}"
    fi
fi

# Kill Python server
kill $PY_PID 2>/dev/null || true
wait $PY_PID 2>/dev/null || true
sleep 1

# ==============================================
echo ""
echo -e "${YELLOW}Test 3: Mixed Clients → Python Server${NC}"
echo "--------------------------------------"

echo "Starting Python server..."
python3 jrpc_oo/tests/test_interop_py_server.py --timeout=30 &
PY_PID=$!
sleep 3

if ! kill -0 $PY_PID 2>/dev/null; then
    echo -e "${RED}Python server failed to start${NC}"
else
    echo "Connecting JS Client1 (with client→server calls)..."
    node -e "
const JRPCNodeClient = require('./JRPCNodeClient').JRPCNodeClient;
class TestClass {
  uniqueFn1(i, str) { console.log('JS1: unique1 called', i, str); return i+1; }
  commonFn() { return 'Client 1'; }
}
let jrnc = new JRPCNodeClient('ws://127.0.0.1:9000');
jrnc.addClass(new TestClass());

const originalSetupDone = jrnc.setupDone.bind(jrnc);
jrnc.setupDone = async function() {
  originalSetupDone();
  console.log('JS Client1: Testing client→server call...');
  try {
    const result = await jrnc.server['TestClass.fn1']();
    console.log('JS Client1: fn1() returned:', result);
    if (result && result.includes('fn1')) {
      console.log('JS_CLIENT1_SERVER_CALL_OK');
    }
  } catch (err) {
    console.log('JS Client1: Error calling server:', err.message);
  }
};
" 2>&1 | tee /tmp/test3_client1.txt &
    CLIENT1_PID=$!
    sleep 3
    
    echo "Connecting JS Client2 (with client→server calls)..."
    node -e "
const JRPCNodeClient = require('./JRPCNodeClient').JRPCNodeClient;
class TestClass {
  uniqueFn2(i) { console.log('JS2: unique2 called', i); return i+1; }
  commonFn() { return 'Client 2'; }
}
let jrnc = new JRPCNodeClient('ws://127.0.0.1:9000');
jrnc.addClass(new TestClass());

const originalSetupDone = jrnc.setupDone.bind(jrnc);
jrnc.setupDone = async function() {
  originalSetupDone();
  console.log('JS Client2: Testing client→server call...');
  try {
    const result = await jrnc.server['TestClass.fn2'](99, {x: 1});
    console.log('JS Client2: fn2() returned:', result);
    if (result === 99) {
      console.log('JS_CLIENT2_SERVER_CALL_OK');
    }
  } catch (err) {
    console.log('JS Client2: Error calling server:', err.message);
  }
};
" 2>&1 | tee /tmp/test3_client2.txt &
    CLIENT2_PID=$!
    sleep 3
    
    echo "Connecting Python client (with client→server calls)..."
    python3 -c "
import asyncio
import sys
sys.path.insert(0, '.')
from jrpc_oo.JRPCClient import JRPCClient

class PyClient:
    def py_method(self):
        return 'python_client'
    def commonFn(self):
        return 'Python Client'

async def main():
    client = JRPCClient('ws://127.0.0.1:9000')
    client.add_class(PyClient(), 'TestClass')
    
    connect_task = asyncio.create_task(client.connect())
    
    # Wait for connection
    for _ in range(50):
        await asyncio.sleep(0.1)
        if client.connected and client.server:
            break
    
    if client.connected and client.server:
        print('Python client: Testing client→server calls...')
        try:
            result = await client.server['TestClass.fn3']({'from': 'python'})
            print(f'Python client: fn3() returned: {result}')
            if 'fn3' in str(result):
                print('PY_CLIENT_SERVER_CALL_OK')
        except Exception as e:
            print(f'Python client: Error calling server: {e}')
    
    await asyncio.sleep(8)  # Stay connected for server→client tests
    await client.disconnect()
    connect_task.cancel()

asyncio.run(main())
" 2>&1 | tee /tmp/test3_pyclient.txt &
    PYCLIENT_PID=$!
    
    # Wait for all tests to complete
    sleep 15
    
    # Cleanup clients
    kill $CLIENT1_PID $CLIENT2_PID $PYCLIENT_PID 2>/dev/null || true
    wait $CLIENT1_PID $CLIENT2_PID $PYCLIENT_PID 2>/dev/null || true
    
    # Check results
    TEST3_CHECKS=0
    TEST3_PASSED=0
    
    # Check JS Client1 called server
    TEST3_CHECKS=$((TEST3_CHECKS + 1))
    if grep -q "JS_CLIENT1_SERVER_CALL_OK" /tmp/test3_client1.txt 2>/dev/null; then
        echo "  ✓ JS Client1 → Python Server: OK"
        TEST3_PASSED=$((TEST3_PASSED + 1))
    else
        echo "  ✗ JS Client1 → Python Server: FAILED"
    fi
    
    # Check JS Client2 called server
    TEST3_CHECKS=$((TEST3_CHECKS + 1))
    if grep -q "JS_CLIENT2_SERVER_CALL_OK" /tmp/test3_client2.txt 2>/dev/null; then
        echo "  ✓ JS Client2 → Python Server: OK"
        TEST3_PASSED=$((TEST3_PASSED + 1))
    else
        echo "  ✗ JS Client2 → Python Server: FAILED"
    fi
    
    # Check Python client called server
    TEST3_CHECKS=$((TEST3_CHECKS + 1))
    if grep -q "PY_CLIENT_SERVER_CALL_OK" /tmp/test3_pyclient.txt 2>/dev/null; then
        echo "  ✓ Python Client → Python Server: OK"
        TEST3_PASSED=$((TEST3_PASSED + 1))
    else
        echo "  ✗ Python Client → Python Server: FAILED"
    fi
    
    # Server→client tests are done by test_interop_py_server.py (auto_test=True by default)
    # Check if server reported success
    
    if [ $TEST3_PASSED -eq $TEST3_CHECKS ]; then
        TEST3_RESULT=0
        echo -e "${GREEN}Test 3: All client→server calls succeeded ✓${NC}"
    else
        echo -e "${RED}Test 3: $TEST3_PASSED/$TEST3_CHECKS client→server calls succeeded${NC}"
    fi
fi

# Kill Python server  
kill $PY_PID 2>/dev/null || true
wait $PY_PID 2>/dev/null || true

# ==============================================
echo ""
echo -e "${YELLOW}Test 4: JS Server → Python Client${NC}"
echo "----------------------------------"

echo "Starting JS interop test server..."
node tests/JRPCServerTestInterop.js 2>&1 | tee /tmp/test4_server.txt &
JS_PID=$!
sleep 3

if ! kill -0 $JS_PID 2>/dev/null; then
    echo -e "${RED}JS server failed to start${NC}"
else
    echo "Running Python client (exposing methods for JS to call)..."
    timeout 15 python3 jrpc_oo/tests/test_interop_js_server_reverse.py 2>&1 | tee /tmp/test4_client.txt &
    PYCLIENT_PID=$!
    
    # Wait for tests to complete
    wait $JS_PID 2>/dev/null
    JS_EXIT=$?
    
    # Check if JS server tests passed
    if grep -q "JS_SERVER_CLIENT_CALLS_OK" /tmp/test4_server.txt 2>/dev/null; then
        TEST4_RESULT=0
        echo -e "${GREEN}Test 4: JS server called Python client methods ✓${NC}"
    else
        echo -e "${RED}Test 4: JS server→Python client calls failed${NC}"
    fi
    
    # Cleanup
    kill $PYCLIENT_PID 2>/dev/null || true
fi

# Kill any remaining processes
kill $JS_PID 2>/dev/null || true
wait 2>/dev/null || true
sleep 1

# ==============================================
echo ""
echo "=============================================="
echo "Interop Test Summary"
echo "=============================================="

TOTAL_PASSED=0
TOTAL_FAILED=0

if [ $TEST1_RESULT -eq 0 ]; then
    echo -e "Test 1 (Python client → JS server):    ${GREEN}PASSED ✓${NC}"
    ((TOTAL_PASSED++))
else
    echo -e "Test 1 (Python client → JS server):    ${RED}FAILED ✗${NC}"
    ((TOTAL_FAILED++))
fi

if [ $TEST2_RESULT -eq 0 ]; then
    echo -e "Test 2 (JS client → Python server):    ${GREEN}PASSED ✓${NC}"
    ((TOTAL_PASSED++))
else
    echo -e "Test 2 (JS client → Python server):    ${RED}FAILED ✗${NC}"
    ((TOTAL_FAILED++))
fi

if [ $TEST3_RESULT -eq 0 ]; then
    echo -e "Test 3 (Mixed clients → Python server): ${GREEN}PASSED ✓${NC}"
    ((TOTAL_PASSED++))
else
    echo -e "Test 3 (Mixed clients → Python server): ${RED}FAILED ✗${NC}"
    ((TOTAL_FAILED++))
fi

if [ $TEST4_RESULT -eq 0 ]; then
    echo -e "Test 4 (JS server → Python client):     ${GREEN}PASSED ✓${NC}"
    ((TOTAL_PASSED++))
else
    echo -e "Test 4 (JS server → Python client):     ${RED}FAILED ✗${NC}"
    ((TOTAL_FAILED++))
fi

echo "=============================================="
echo "Total: $TOTAL_PASSED passed, $TOTAL_FAILED failed"
echo "=============================================="

# Exit with failure if any test failed
[ $TOTAL_FAILED -eq 0 ]

#!/usr/bin/env python3
"""
Cross-language interop test: Python server for JavaScript client.

Usage:
1. Run this server: python jrpc_oo/tests/test_interop_py_server.py
2. In another terminal, run JS client: node tests/Client1.js

Expected: JS client can call Python server methods and receive correct responses.

The server will automatically test calling client methods after connection.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from jrpc_oo.JRPCServer import JRPCServer
from jrpc_oo.JRPCCommon import RPCMethodNotFoundError


class TestClass:
    """Test class matching JS server's TestClass interface."""
    
    def __init__(self):
        self.test = 1
        self.call_count = 0
        self.server_ref = None
    
    def fn1(self, args=None):
        """Match JS TestClass.fn1."""
        print(f"fn1 called with args={args}")
        self.call_count += 1
        return "this is fn1 from Python"
    
    def fn2(self, arg1, arg2):
        """Match JS TestClass.fn2."""
        print(f"fn2 called with arg1={arg1}, arg2={arg2}")
        self.call_count += 1
        return arg1
    
    def fn3(self, args):
        """Match JS TestClass2.fn3."""
        print(f"fn3 called with args={args}")
        self.call_count += 1
        return "this is fn3 from Python"
    
    def echoBack(self, args):
        """Match JS TestClass.echoBack."""
        print(f"echoBack called with args={args}")
        self.call_count += 1
        return "Python returning done"


async def test_client_methods(server, test_class):
    """Test calling methods on connected JS clients."""
    print()
    print("Testing server → client calls...")
    print("-" * 40)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test calling uniqueFn1 (Client1 has this)
    try:
        if 'TestClass.uniqueFn1' in server.call:
            results = await server.call['TestClass.uniqueFn1'](42, 'hello from Python')
            print(f"  uniqueFn1(42, 'hello') returned: {results}")
            # Should return 43 (i + 1)
            for uuid, result in results.items():
                if result == 43:
                    print(f"    ✓ Client {uuid[:8]}... returned correct value")
                    tests_passed += 1
                else:
                    print(f"    ✗ Client {uuid[:8]}... returned {result}, expected 43")
                    tests_failed += 1
        else:
            print("  uniqueFn1 not available (Client1 not connected?)")
    except RPCMethodNotFoundError:
        print("  uniqueFn1 not found (Client1 not connected)")
    except Exception as e:
        print(f"  uniqueFn1 error: {e}")
        tests_failed += 1
    
    # Test calling uniqueFn2 (Client2 has this)
    try:
        if 'TestClass.uniqueFn2' in server.call:
            results = await server.call['TestClass.uniqueFn2'](100, 'test')
            print(f"  uniqueFn2(100, 'test') returned: {results}")
            for uuid, result in results.items():
                if result == 101:
                    print(f"    ✓ Client {uuid[:8]}... returned correct value")
                    tests_passed += 1
                else:
                    print(f"    ✗ Client {uuid[:8]}... returned {result}, expected 101")
                    tests_failed += 1
        else:
            print("  uniqueFn2 not available (Client2 not connected?)")
    except RPCMethodNotFoundError:
        print("  uniqueFn2 not found (Client2 not connected)")
    except Exception as e:
        print(f"  uniqueFn2 error: {e}")
        tests_failed += 1
    
    # Test calling commonFn (both clients have this)
    try:
        if 'TestClass.commonFn' in server.call:
            results = await server.call['TestClass.commonFn']()
            print(f"  commonFn() returned: {results}")
            for uuid, result in results.items():
                # Accept Client 1, Client 2, or Python Client as valid responses
                if result in ['Client 1', 'Client 2', 'Python Client']:
                    print(f"    ✓ Client {uuid[:8]}... identified as '{result}'")
                    tests_passed += 1
                else:
                    print(f"    ✗ Client {uuid[:8]}... returned unexpected: {result}")
                    tests_failed += 1
        else:
            print("  commonFn not available (no clients connected?)")
    except RPCMethodNotFoundError:
        print("  commonFn not found (no clients connected)")
    except Exception as e:
        print(f"  commonFn error: {e}")
        tests_failed += 1
    
    print("-" * 40)
    print(f"Server→Client tests: {tests_passed} passed, {tests_failed} failed")
    return tests_passed, tests_failed


async def run_server(auto_test: bool = True, timeout: int = 0):
    """Run the interop test server.
    
    Args:
        auto_test: If True, automatically test client methods when clients connect
        timeout: If > 0, exit after this many seconds (for automated testing)
    """
    print("=" * 60)
    print("Cross-Language Interop Test: Python Server for JS Client")
    print("=" * 60)
    print()
    
    server = JRPCServer(port=9000)
    test_class = TestClass()
    test_class.server_ref = server
    server.add_class(test_class, "TestClass")
    
    await server.start()
    
    print("Server started on ws://127.0.0.1:9000")
    print()
    print("Exposed methods:")
    if hasattr(server, 'classes') and server.classes:
        for cls_obj in server.classes:
            for method_name in cls_obj.keys():
                print(f"  - {method_name}")
    print()
    print("Waiting for JS client connections...")
    print("Run in another terminal:")
    print("  node tests/Client1.js    # For Client 1")
    print("  node tests/Client2.js    # For Client 2 (optional)")
    print()
    if timeout > 0:
        print(f"Will auto-exit after {timeout} seconds")
    else:
        print("Press Ctrl+C to stop")
    print()
    
    start_time = asyncio.get_event_loop().time()
    last_client_count = 0
    tests_run = False
    total_passed = 0
    total_failed = 0
    
    try:
        while True:
            await asyncio.sleep(2)
            
            current_time = asyncio.get_event_loop().time()
            elapsed = current_time - start_time
            
            # Check timeout
            if timeout > 0 and elapsed > timeout:
                print(f"\nTimeout reached ({timeout}s)")
                break
            
            # Report status
            if server.remotes:
                client_count = len(server.remotes)
                print(f"[{elapsed:.0f}s] Connected clients: {client_count}, calls received: {test_class.call_count}")
                
                # Auto-test when new clients connect
                if auto_test and client_count > last_client_count:
                    await asyncio.sleep(1)  # Let setup complete
                    passed, failed = await test_client_methods(server, test_class)
                    total_passed += passed
                    total_failed += failed
                    tests_run = True
                
                last_client_count = client_count
            
    except KeyboardInterrupt:
        print()
        print("Shutting down...")
    finally:
        await server.stop()
    
    print()
    print("=" * 60)
    print("Summary:")
    print(f"  Client→Server calls received: {test_class.call_count}")
    if tests_run:
        print(f"  Server→Client tests: {total_passed} passed, {total_failed} failed")
    if test_class.call_count > 0:
        print("  ✓ Client→Server: WORKING")
    else:
        print("  ✗ Client→Server: No calls received")
    if tests_run and total_failed == 0 and total_passed > 0:
        print("  ✓ Server→Client: WORKING")
    elif tests_run:
        print("  ✗ Server→Client: Some tests failed")
    print("=" * 60)
    
    return test_class.call_count > 0 and (not tests_run or total_failed == 0)


if __name__ == "__main__":
    # Parse args
    timeout = 0
    auto_test = True
    
    for arg in sys.argv[1:]:
        if arg.startswith('--timeout='):
            timeout = int(arg.split('=')[1])
        elif arg == '--no-auto-test':
            auto_test = False
    
    success = asyncio.run(run_server(auto_test=auto_test, timeout=timeout))
    sys.exit(0 if success else 1)

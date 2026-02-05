#!/usr/bin/env python3
"""
Cross-language interop test: Python client connecting to JavaScript server.

Usage:
1. Start JS server: node JRPCServerTest.js no_wss
2. Run this test: python jrpc_oo/tests/test_interop_js_server.py

Expected: Python client can call JS server methods and receive correct responses.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from jrpc_oo.JRPCClient import JRPCClient


class PythonTestClient:
    """Client class to expose methods to JS server."""
    
    def python_echo(self, message):
        """Echo from Python client."""
        return f"python_echo: {message}"
    
    def get_client_type(self):
        """Identify this client."""
        return "python"


async def run_interop_test():
    """Run the interop test against JS server."""
    print("=" * 60)
    print("Cross-Language Interop Test: Python Client → JS Server")
    print("=" * 60)
    print()
    print("Connecting to ws://127.0.0.1:9000...")
    
    client = JRPCClient("ws://127.0.0.1:9000")
    test_class = PythonTestClient()
    client.add_class(test_class, "PythonTestClient")
    
    # Start connection in background
    connect_task = asyncio.create_task(client.connect())
    
    # Wait for connection and setup
    connected = False
    for _ in range(50):  # 5 second timeout
        await asyncio.sleep(0.1)
        if client.connected and client.server:
            connected = True
            break
    
    if not connected:
        print("FAILED: Could not connect to JS server")
        print("Make sure JS server is running: node JRPCServerTest.js no_wss")
        return False
    
    print("Connected!")
    print()
    print("Available server methods:")
    for method in sorted(client.server.keys()):
        print(f"  - {method}")
    print()
    
    # Run tests
    all_passed = True
    
    # Test 1: Call fn1 (no args)
    print("Test 1: Calling TestClass.fn1() or TestClass2.fn1()...")
    try:
        # JS server uses TestClass2 which extends TestClass
        fn1_method = None
        for m in client.server.keys():
            if 'fn1' in m.lower():
                fn1_method = m
                break
        
        if fn1_method:
            result = await client.server[fn1_method]()
            print(f"  Result: {result}")
            if 'fn1' in str(result).lower():
                print("  ✓ PASSED")
            else:
                print("  ✗ FAILED: Unexpected result")
                all_passed = False
        else:
            print("  ✗ FAILED: fn1 method not found")
            all_passed = False
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        all_passed = False
    print()
    
    # Test 2: Call fn2 with args
    print("Test 2: Calling TestClass.fn2(1, {'key': 'value'})...")
    try:
        fn2_method = None
        for m in client.server.keys():
            if 'fn2' in m.lower():
                fn2_method = m
                break
        
        if fn2_method:
            result = await client.server[fn2_method](1, {'key': 'value'})
            print(f"  Result: {result}")
            if result == 1:  # fn2 returns arg1
                print("  ✓ PASSED")
            else:
                print("  ✗ FAILED: Expected 1, got {result}")
                all_passed = False
        else:
            print("  ✗ FAILED: fn2 method not found")
            all_passed = False
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        all_passed = False
    print()
    
    # Test 3: Call fn3 (from TestClass2)
    print("Test 3: Calling TestClass2.fn3({'test': 'data'})...")
    try:
        fn3_method = None
        for m in client.server.keys():
            if 'fn3' in m.lower():
                fn3_method = m
                break
        
        if fn3_method:
            result = await client.server[fn3_method]({'test': 'data'})
            print(f"  Result: {result}")
            if 'fn3' in str(result).lower():
                print("  ✓ PASSED")
            else:
                print("  ✗ FAILED: Unexpected result")
                all_passed = False
        else:
            print("  ✗ FAILED: fn3 method not found")
            all_passed = False
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        all_passed = False
    print()
    
    # Summary
    print("=" * 60)
    if all_passed:
        print("ALL TESTS PASSED ✓")
    else:
        print("SOME TESTS FAILED ✗")
    print("=" * 60)
    
    # Cleanup
    await client.disconnect()
    connect_task.cancel()
    try:
        await connect_task
    except asyncio.CancelledError:
        pass
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(run_interop_test())
    sys.exit(0 if success else 1)

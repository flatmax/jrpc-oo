#!/usr/bin/env python3
"""
Test client for JRPCServerTest.js server
Tests RPC methods exposed by the JavaScript server
"""
from jrpc_client import JRPCClient
import time
import json
import sys

class TestClient:
    """Test client for JRPCServerTest.js server"""
    
    def __init__(self):
        """Initialize the test client"""
        self.client = JRPCClient(port=9000, debug=True)
        self.received_echo = False
    
    def connect(self):
        """Connect to the JavaScript RPC server"""
        print("\nAttempting to connect to JavaScript server...")
        connected = self.client.connect()
        if not connected:
            print("Failed to connect to server")
            return False
        
        # Wait for connection to be fully ready
        self.client.connection_ready_event.wait()
        print("\nConnection fully established!")
        print(self.client.server)
        return True
    
    def test_fn1(self):
        """Test the fn1 method (no arguments)"""
        print("\nTesting TestClass.fn1...")
        try:
            result = self.client.server['TestClass.fn1']()
            print(f"Result: {result}")
            assert result == "this is fn1", f"Expected 'this is fn1', got '{result}'"
            print("✓ TestClass.fn1 test passed")
            return True
        except Exception as e:
            print(f"✗ TestClass.fn1 test failed: {e}")
            return False
    
    def test_fn2(self):
        """Test the fn2 method (with arguments)"""
        print("\nTesting TestClass.fn2...")
        try:
            arg1 = 1
            arg2 = {'0': 'test', '1': [1, 2], '2': 'this function'}
            result = self.client.server['TestClass.fn2'](arg1, arg2)
            print(f"Result: {result}")
            assert result == arg1, f"Expected {arg1}, got '{result}'"
            print("✓ TestClass.fn2 test passed")
            return True
        except Exception as e:
            print(f"✗ TestClass.fn2 test failed: {e}")
            return False
    
    def test_fn3(self):
        """Test the fn3 method"""
        print("\nTesting TestClass2.fn3...")
        try:
            arg = {'test': 'data', 'array': [1, 2, 3]}
            result = self.client.server['TestClass2.fn3'](arg)
            print(f"Result: {result}")
            assert result == "this is fn3", f"Expected 'this is fn3', got '{result}'"
            print("✓ TestClass2.fn3 test passed")
            return True
        except Exception as e:
            print(f"✗ TestClass2.fn3 test failed: {e}")
            return False
    
    def echoBack(self, args):
        """Echo back handler - will be called by server"""
        print(f"\nReceived echo from server: {args}")
        self.received_echo = True
        return "Python client received echo"
    
    def test_echo(self):
        """Test the echoBack method"""
        print("\nTesting TestClass.echoBack...")
        try:
            # First, make sure our class is registered to handle callbacks
            self.client.add_class(self)
            
            # Send echo request to server
            result = self.client.server['TestClass.echoBack']("Python client testing echo")
            print(f"Initial result: {result}")
            
            # Wait for server to call back our echoBack method
            timeout = 5
            start_time = time.time()
            while not self.received_echo and time.time() - start_time < timeout:
                time.sleep(0.1)
            
            if not self.received_echo:
                raise TimeoutError("Timeout waiting for server to call echoBack")
            
            print("✓ TestClass.echoBack test passed")
            return True
        except Exception as e:
            print(f"✗ TestClass.echoBack test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests and report results"""
        if not self.connect():
            return False
        
        results = []
        results.append(("TestClass.fn1", self.test_fn1()))
        results.append(("TestClass.fn2", self.test_fn2()))
        results.append(("TestClass2.fn3", self.test_fn3()))
        results.append(("TestClass.echoBack", self.test_echo()))
        
        # Print summary
        print("\n" + "="*40)
        print("Test Results Summary:")
        print("="*40)
        
        all_passed = True
        for name, passed in results:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status} : {name}")
            if not passed:
                all_passed = False
        
        print("="*40)
        print(f"Overall result: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
        
        return all_passed

if __name__ == "__main__":
    print("Starting JavaScript server test client...")
    print("Note: Make sure JRPCServerTest.js is running")
    
    # Give a moment for any instructions to be read
    time.sleep(1)
    
    client = TestClient()
    success = client.run_all_tests()
    
    # Close the client connection
    client.client.close()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

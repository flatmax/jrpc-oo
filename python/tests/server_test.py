#!/usr/bin/env python3
"""
Test server for JRPC-OO Python implementation.
Similar to JRPCServerTestConcurrent.js
"""

import time
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from JRPCServer import JRPCServer

class TestClass:
    """Test class with methods to expose over RPC."""
    
    def __init__(self):
        """Initialize test class."""
        self.test = 1
        self.i = 0
    
    def fn1(self, args):
        """Test function similar to JavaScript version."""
        print("this is fn1")
        print("got args")
        print(args)
        print(f"args={args}")
        return "this is fn1"
    
    def multi_client_test(self, jrpc_server):
        """Test function that calls methods on multiple clients."""
        print("multiClientTest : enter")
        
        try:
            # Define handler functions for each step
            def handle_uniqueFn1_result(res):
                if len(res) > 1:
                    raise Exception("Expected only one remote to be called")
                remote_id = list(res.keys())[0]
                value = list(res.values())[0]
                print(f"remote : {remote_id} returns {value}")
                return jrpc_server.call['TestClass.uniqueFn2'](value, 'hi there 2')
            
            def handle_uniqueFn2_result(res):
                if len(res) > 1:
                    raise Exception("Expected only one remote to be called")
                remote_id = list(res.keys())[0]
                value = list(res.values())[0]
                print(f"remote : {remote_id} returns {value}")
                return jrpc_server.call['TestClass.commonFn'](value, 'common Fn')
            
            def print_final_result(data):
                print("commonFn returns")
                print(data)
            
            def handle_error(e):
                print("multiClientTest : error ")
                print(e)
            
            # Start the promise chain
            jrpc_server.call['TestClass.uniqueFn1'](self.i, 'hi there 1').then(
                handle_uniqueFn1_result
            ).then(
                handle_uniqueFn2_result
            ).then(
                print_final_result
            ).catch(
                handle_error
            )
            
            self.i += 1
            
        except Exception as e:
            print(f"multiClientTest error: {e}")
    
if __name__ == "__main__":
    # Create server on port 9000
    jrpc_server = JRPCServer(9000)
    
    # Create test class instance
    tc = TestClass()
    
    # Add the class to the server
    jrpc_server.add_class(tc)
    
    # Start the server
    server_thread = jrpc_server.start()
    
    # Run the multi-client test every second
    try:
        while True:
            tc.multi_client_test(jrpc_server)
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server stopped")

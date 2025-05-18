#!/usr/bin/env python3
"""
Example JRPC server for testing the Python implementation.
Similar to JRPCServerTestConcurrent.js
"""

import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from jrpc_oo.JRPCServer import JRPCServer


class JRPCTestServer(JRPCServer):
    """Server class that tracks remote connections"""
    def __init__(self, port=9000, remote_timeout=60):
        super().__init__(port, remote_timeout)
        self.has_remote = False
        self.functions_ready = False
        self.required_functions = ['TestClass.uniqueFn1', 'TestClass.uniqueFn2', 'TestClass.commonFn']
    
    def remote_is_up(self):
        """Override to mark when a remote connects"""
        super().remote_is_up()
        self.has_remote = True
        print("First client connected!")
    
    def setup_done(self):
        """Called when remote functions are set up"""
        super().setup_done()
        
        # Check if any of the required functions are available
        # We'll test with whatever function is available first
        available_funcs = 0
        for func in self.required_functions:
            if func in self.call:
                available_funcs += 1
                
        if available_funcs > 0:
            # We have at least some functions available
            print(f"Found {available_funcs} required functions, ready to start testing")
            self.functions_ready = True
        
        if all_ready:
            print("All required remote functions are available!")
            self.functions_ready = True
        else:
            available = list(self.call.keys())
            print(f"Waiting for functions: {[f for f in self.required_functions if f not in available]}")


class TestClass:
    def __init__(self):
        self.test = 1
        self.i = 0
    
    def fn1(self, args):
        """Test function that echoes arguments"""
        print('this is fn1')
        print('got args:', args)
        return 'this is fn1'
    
    def multi_client_test(self, jrpc_server):
        """Test calling functions across multiple clients"""
        print('multiClientTest: enter')
        
        def on_unique_fn1(results):
            if len(results.keys()) > 1:
                print("Error: Expected only one remote to be called")
                return None
                
            i = None
            for v, result in results.items():
                print(f'remote: {v} returns {result}')
                i = result
            
            if i is not None:
                return jrpc_server.call['TestClass.uniqueFn2'](i, 'hi there 2')
            return None
            
        def on_unique_fn2(results):
            if len(results.keys()) > 1:
                print("Error: Expected only one remote to be called")
                return None
                
            i = None
            for v, result in results.items():
                print(f'remote: {v} returns {result}')
                i = result
            
            if i is not None:
                return jrpc_server.call['TestClass.commonFn'](i, 'common Fn')
            return None
            
        def on_common_fn(results):
            print('commonFn returns:')
            print(results)
            
        def on_error(err):
            print('multiClientTest: error')
            print(err)
            
        # Chain of calls
        jrpc_server.call['TestClass.uniqueFn1'](self.i, 'hi there 1') \
            .then(on_unique_fn1) \
            .then(on_unique_fn2) \
            .then(on_common_fn) \
            .catch(on_error)
            
        self.i += 1

if __name__ == "__main__":
    # Create server on port 9000
    jrpc_server = JRPCTestServer(port=9000)
    
    # Create test class instance and add it
    tc = TestClass()
    jrpc_server.add_class(tc)
    
    # Start server in a non-blocking way
    jrpc_server.start(blocking=False)
    
    print("Server running on port 9000")
    print("Waiting for clients to connect...")
    
    # Run the multi-client test periodically, but only when required functions are ready
    try:
        while True:
            time.sleep(1)
            if jrpc_server.functions_ready:
                tc.multi_client_test(jrpc_server)
            elif jrpc_server.has_remote:
                print("Remote connected but waiting for functions to be ready...")
    except KeyboardInterrupt:
        print("\nShutting down server")
        jrpc_server.stop()

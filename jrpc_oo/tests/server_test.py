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
        # Check if we already have required functions
        self.check_required_functions()
    
    def check_required_functions(self):
        """Check if required functions are available"""
        # Get all available functions
        available = list(self.call.keys()) if hasattr(self, 'call') and self.call else []
        
        # Check if any of the required functions are available
        available_funcs = 0
        for func in self.required_functions:
            if func in available:
                available_funcs += 1
                print(f"Required function found: {func}")
            
        if available_funcs > 0:
            # We have at least some functions available
            print(f"Found {available_funcs}/{len(self.required_functions)} required functions, ready to start testing")
            self.functions_ready = True
            
            # Print which functions are still missing
            missing = [f for f in self.required_functions if f not in available]
            if missing:
                print(f"Still waiting for optional functions: {missing}")
            else:
                print("All required remote functions are available!")
        else:
            # No required functions available yet
            print(f"Waiting for functions: {self.required_functions}")
            self.functions_ready = False
    
    def setup_done(self):
        """Called when remote functions are set up"""
        super().setup_done()
        
        # Check if required functions are available
        self.check_required_functions()


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
        # Try to run this immediately after all other initialization, 
        # in case functions are already registered
        jrpc_server.check_required_functions()
        
        while True:
            time.sleep(1)
            
            if jrpc_server.functions_ready:
                print("Running multi-client test with available functions...")
                tc.multi_client_test(jrpc_server)
            elif jrpc_server.has_remote:
                # Recheck if functions have become available
                jrpc_server.check_required_functions()
                
                if not jrpc_server.functions_ready:
                    print("Remote connected but waiting for functions to be ready...")
    except KeyboardInterrupt:
        print("\nShutting down server")
        jrpc_server.stop()

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
    
    def remote_is_up(self):
        """Override to mark when a remote connects"""
        super().remote_is_up()
        self.has_remote = True
        print("First client connected!")


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
    
    # Run the multi-client test periodically, but only when a client is connected
    try:
        while True:
            time.sleep(1)
            if jrpc_server.has_remote:
                tc.multi_client_test(jrpc_server)
    except KeyboardInterrupt:
        print("\nShutting down server")
        jrpc_server.stop()

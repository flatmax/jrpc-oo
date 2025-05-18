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
    def __init__(self, port=9000, remote_timeout=10):  # Reduced timeout
        super().__init__(port, remote_timeout)
        self.has_remote = False
        self.functions_ready = False
        self.required_functions = ['TestClass.uniqueFn1', 'TestClass.uniqueFn2', 'TestClass.commonFn']
        # Add explicit initialization of _last_sync_time for this subclass
        self._last_sync_time = {}
    
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
        
        # Check which functions are available
        available_functions = list(jrpc_server.call.keys())
        print(f"Available functions for testing: {available_functions}")
        
        # Define our chain callbacks
        def on_unique_fn1(results):
            if not results or len(results.keys()) == 0:
                print("No results returned from uniqueFn1")
                return None
                
            if len(results.keys()) > 1:
                print("Warning: Expected only one remote to be called for uniqueFn1")
                
            i = None
            for v, result in results.items():
                print(f'remote: {v} returns {result}')
                i = result
            
            if i is not None and 'TestClass.uniqueFn2' in jrpc_server.call:
                return jrpc_server.call['TestClass.uniqueFn2'](i, 'hi there 2')
            else:
                print("Cannot continue: TestClass.uniqueFn2 function not available or no valid result")
                return None
            
        def on_unique_fn2(results):
            if not results:
                print("No results returned from uniqueFn2")
                return None
                
            if len(results.keys()) > 1:
                print("Warning: Expected only one remote to be called for uniqueFn2")
                
            i = None
            for v, result in results.items():
                print(f'remote: {v} returns {result}')
                i = result
            
            if i is not None and 'TestClass.commonFn' in jrpc_server.call:
                return jrpc_server.call['TestClass.commonFn'](i, 'common Fn')
            else:
                print("Cannot continue: TestClass.commonFn function not available or no valid result")
                return None
            
        def on_common_fn(results):
            if not results:
                print("No results returned from commonFn")
                return
                
            print('commonFn returns:')
            print(results)
            
        def on_error(err):
            print('multiClientTest: error - this is expected during normal operation')
            print(err)
        
        try:
            # Determine which functions to use
            if 'TestClass.uniqueFn1' in jrpc_server.call:
                print("Starting with uniqueFn1")
                # Start with uniqueFn1
                jrpc_server.call['TestClass.uniqueFn1'](self.i, 'hi there 1') \
                    .then(on_unique_fn1) \
                    .then(on_unique_fn2) \
                    .then(on_common_fn) \
                    .catch(on_error)
            elif 'TestClass.uniqueFn2' in jrpc_server.call:
                # Start with uniqueFn2 directly
                print("Starting with uniqueFn2 (uniqueFn1 not available)")
                jrpc_server.call['TestClass.uniqueFn2'](self.i, 'hi there 2') \
                    .then(on_unique_fn2) \
                    .then(on_common_fn) \
                    .catch(on_error)
            elif 'TestClass.commonFn' in jrpc_server.call:
                # Just call commonFn directly
                print("Starting with commonFn (uniqueFn1 and uniqueFn2 not available)")
                jrpc_server.call['TestClass.commonFn'](self.i, 'common Fn') \
                    .then(on_common_fn) \
                    .catch(on_error)
            else:
                print("No remote functions available to test")
                
            self.i += 1
        except Exception as e:
            print(f"Exception during multiClientTest: {str(e)}")
            import traceback
            traceback.print_exc()

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
            
            # First check if we have any connected remotes
            has_connected_remotes = hasattr(jrpc_server, 'remotes') and jrpc_server.remotes
            
            if has_connected_remotes:
                # Get available functions and check if any match our requirements
                available_functions = list(jrpc_server.call.keys()) if hasattr(jrpc_server, 'call') and jrpc_server.call else []
                usable_functions = [f for f in available_functions if f.startswith('TestClass.')]
                
                if usable_functions:
                    # We have at least some useful functions to test with
                    print(f"Running multi-client test with available functions: {usable_functions}")
                    tc.multi_client_test(jrpc_server)
                else:
                    # Recheck if functions have become available
                    jrpc_server.check_required_functions()
                    
                    if not jrpc_server.functions_ready:
                        print("Remote connected but waiting for usable functions...")
                        # Try to actively sync with remotes - but only once every 5 seconds
                        current_time = time.time()
                        for remote_id, remote in jrpc_server.remotes.items():
                            # Make sure _last_sync_time is initialized
                            if not hasattr(jrpc_server, '_last_sync_time'):
                                jrpc_server._last_sync_time = {}
                                
                            # Only sync if we haven't done so recently
                            if remote_id not in jrpc_server._last_sync_time or \
                               current_time - jrpc_server._last_sync_time[remote_id] >= 5:
                                print(f"Requesting components from remote {remote_id}")
                                try:
                                    # Update last sync time
                                    jrpc_server._last_sync_time[remote_id] = current_time
                                    
                                    remote.jrpc.call('system.listComponents', [], lambda err, result: 
                                        print(f"Sync error: {err}") if err else 
                                        jrpc_server.setup_fns(list(result.keys()) if result else [], remote))
                                except Exception as e:
                                    print(f"Error requesting components from remote {remote_id}: {str(e)}")
                            else:
                                print(f"Skipping sync with remote {remote_id} - too soon since last sync")
            else:
                print("No remotes connected, waiting for connections...")
    except KeyboardInterrupt:
        print("\nShutting down server")
        jrpc_server.stop()

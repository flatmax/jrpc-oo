#!/usr/bin/env python3
"""
Test server implementation equivalent to JRPCServerTest.js
"""
import json
import asyncio
from jrpc_server import JRPCServer

class TestClass:
    """Base test class with RPC methods"""
    def __init__(self):
        self.test = 1

    def fn1(self, args=None):
        print('this is fn1')
        print('got args')
        print(args)
        print(f'args={args}')
        return 'this is fn1'

    def fn2(self, *args):
        print('========== fn2 called with: ==========')
        print(f'Number of args: {len(args)}')
        print(f'args type: {type(args)}')
        
        # Print each argument with its type for debugging
        for i, arg in enumerate(args):
            print(f'Arg {i} type: {type(arg)}')
            if isinstance(arg, (dict, list)):
                print(f'Arg {i} value: {json.dumps(arg, indent=2)}')
            else:
                print(f'Arg {i} value: {arg}')
        
        print('=======================================')
                
        if args:
            return args[0]  # Return the first argument as per JS expectation
        return None

    def echoBack(self, args):
        print(self)
        print(f'echoBack {args}')
        # Get the RPC instance to make calls back to the client
        rpc = self.rpc
        if not rpc:
            print("No RPC instance available")
            return 'No RPC connection'
            
        # Create request for callback
        request, _ = rpc.create_request('LocalJRPC.echoBack', {'args': ['python responding']})
        
        try:
            # Send through the appropriate server mechanism
            print(f"Sending echo back to client")
            if hasattr(rpc, 'server') and hasattr(rpc.server, 'send_message'):
                # Make sure we have a valid client reference
                if hasattr(rpc, 'ws'):
                    rpc.server.send_message(rpc.ws, json.dumps(request))
                else:
                    print("No client WebSocket connection available")
            else:
                print("Server not properly initialized for sending")
        except Exception as e:
            print(f"Error sending echo back: {str(e)}")
            import traceback
            print(traceback.format_exc())
            
        return 'python returning done'

    def set_rpc(self, rpc):
        """Store RPC instance for making calls back to client"""
        self.rpc = rpc
        
    def get_remotes(self):
        """Get RPC instances for callbacks"""
        return [self.rpc]


class TestClass2(TestClass):
    """Extended test class with additional method"""
    def fn3(self, args):
        print(json.dumps(args, indent=2))
        return 'this is fn3'


if __name__ == '__main__':
    # Create test class instances
    tc2 = TestClass2()

    # Start server on port 9000 with debug logging enabled
    server = JRPCServer(port=9000, debug=True)
    server.add_class(tc2, 'TestClass')  # Register as TestClass for compatibility
    server.add_class(tc2, 'TestClass2') # Also register as TestClass2
    
    try:
        print("Starting RPC server...")
        server.start()
    except KeyboardInterrupt:
        print("Server stopped")

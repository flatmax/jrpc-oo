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

    async def fn1(self, args=None):
        print('this is fn1')
        print('got args')
        print(args)
        print(f'args={args}')
        return 'this is fn1'

    async def fn2(self, *args):
        print('fn2')
        if args:
            print('arg1:', json.dumps(args[0], indent=2))
            if len(args) > 1:
                print('arg2:', json.dumps(args[1], indent=2))
            return args[0]  # Return the first argument as per JS expectation
        return None

    async def echoBack(self, args):
        print(self)
        print(f'echoBack {args}')
        # Schedule callback after 1 second
        await asyncio.sleep(1)
        # Get the RPC instance to make calls back to the client
        rpc = self.get_remotes()[0]
        # Create request for callback
        request, _ = rpc.create_request('LocalJRPC.echoBack', {'args': ['python responding']})
        # Send request through websocket
        await rpc.ws.send(json.dumps(request))
        return 'python returning done'

    def set_rpc(self, rpc):
        """Store RPC instance for making calls back to client"""
        self.rpc = rpc
        
    def get_remotes(self):
        """Get RPC instances for callbacks"""
        return [self.rpc]


class TestClass2(TestClass):
    """Extended test class with additional method"""
    async def fn3(self, args):
        print(json.dumps(args, indent=2))
        return 'this is fn3'


if __name__ == '__main__':
    # Create test class instances
    tc2 = TestClass2()

    # Start server on port 9000 with debug logging enabled
    server = JRPCServer(port=9000, debug=False)
    server.add_class(tc2, 'TestClass')  # Register as TestClass for compatibility
    server.add_class(tc2, 'TestClass2') # Also register as TestClass2
    server.start()
    server.serve_forever()

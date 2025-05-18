#!/usr/bin/env python3
"""
Python equivalent of the local-jrpc.js client.
"""
import asyncio
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from jrpc_oo.JRPCClient import JRPCClient


class LocalJRPC(JRPCClient):
    """Python equivalent of LocalJRPC from local-jrpc.js."""
    
    def __init__(self, server_uri='ws://0.0.0.0:9000'):
        """Initialize the LocalJRPC client."""
        super().__init__(server_uri=server_uri, remote_timeout=300)
        self.debug = False
    
    def setup_done(self):
        """Called when server connection is established."""
        print(f"Server connected, available methods: {list(self.server.keys())}")
        self.add_class(self)
        
        # Test the functions
        asyncio.create_task(self.test_arg_pass())
        
    def remote_is_up(self):
        """Called when remote connection is established."""
        print('LocalJRPC::remote_is_up')
        self.add_class(self)
    
    def setup_skip(self):
        """Called when setup fails."""
        super().setup_skip()
        print('Is JRPC-OO server running?')
        print('Is the ws URL accessible?')
    
    async def test_arg_pass(self):
        """Test passing arguments to server methods."""
        print(">>> Testing TestClass.fn2 with arguments")
        
        if 'TestClass.fn2' in self.server:
            # Create test arguments
            arg1 = 1
            arg2 = {"0": "test", "1": [1, 2], "2": "this function"}
            
            print('>>> Sending request to TestClass.fn2:')
            print(f'Arguments: [{arg1}, {arg2}]')
            
            try:
                result = await self.server['TestClass.fn2'](arg1, arg2)
                print(f'<<< Received response: {result}')
            except Exception as e:
                print(f"Error occurred: {e}")
        else:
            print("TestClass.fn2 not found in server methods!")
            print(f"Available methods: {list(self.server.keys())}")
            print("Expected the server to expose a class TestClass with function fn2 but couldn't find it")
        
        # Test function with no arguments
        await self.test_no_arg_pass()
        
    async def test_no_arg_pass(self):
        """Test calling server method with no arguments."""
        print(">>> Testing TestClass.fn1 with no arguments")
        
        if 'TestClass.fn1' in self.server:
            try:
                result = await self.server['TestClass.fn1']()
                print(f'<<< Received response: {result}')
            except Exception as e:
                print(f"Error occurred: {e}")
        else:
            print("TestClass.fn1 not found in server methods!")
            print("Expected the server to expose a class TestClass with function fn1 but couldn't find it")
        
        # Test echo chamber
        await self.start_echo_chamber()
    
    async def start_echo_chamber(self):
        """Start the echo test."""
        await self.echoBack('you are in an echo chamber')
    
    async def echoBack(self, args):
        """Echo back function that calls the server's echoBack."""
        print(f'echoBack {args}')
        
        if 'TestClass.echoBack' in self.server:
            try:
                result = await self.server['TestClass.echoBack']('this is the browser saying echo')
                print('TestClass.echoBack returned:')
                print(json.dumps(result, indent=2))
            except Exception as e:
                print(f"Error calling TestClass.echoBack: {e}")
        else:
            print("Expected the server to expose a class TestClass with function echoBack but couldn't find it")
        
        return 'echoBack returned you this'


async def main():
    """Main function to run the client."""
    # Parse command-line arguments for server URI
    server_uri = 'ws://0.0.0.0:9000'
    for arg in sys.argv:
        if arg.startswith('ws://') or arg.startswith('wss://'):
            server_uri = arg
    
    # Create client
    client = LocalJRPC(server_uri)
    
    # Connect to server
    await client.connect()
    
    try:
        # Keep client running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Client stopped by user")
    finally:
        if hasattr(client, 'disconnect'):
            await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

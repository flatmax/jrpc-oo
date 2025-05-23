#!/usr/bin/env python3
import asyncio
import sys
from JRPCServer import JRPCServer
from JRPCClient import JRPCClient

class ServerTest:
    def __init__(self):
        self.test = 1
        
    def fn1(self, args):
        print("This is fn1")
        print(f"args={args}")
        return "This is fn1"
        
    def echoBack(self, args):
        print(f"echoBack {args}")
        return "python returning done"


class ClientTest:
    def uniqueFn(self, i, message):
        print(f"uniqueFn called with {i}, {message}")
        return i + 1
        
    def commonFn(self):
        return "Client response"


async def run_server():
    server = JRPCServer(port=9001)
    server_test = ServerTest()
    server.add_class(server_test)
    await server.start()
    return server


async def run_client():
    client = JRPCClient("ws://127.0.0.1:9001")
    client_test = ClientTest()
    client.add_class(client_test)
    await client.connect()
    return client


async def main():
    server = await run_server()
    
    # Give server time to start
    await asyncio.sleep(1)
    
    client = await run_client()
    
    # Give client time to connect and setup
    await asyncio.sleep(2)
    
    if not client.connected:
        print("Client failed to connect")
        await server.stop()
        return
        
    # Test calling server method
    try:
        result = await client.server["ServerTest.fn1"]("test argument")
        print(f"Server method result: {result}")
        
        # Test calling method on all connected remotes
        result = await client.call["ServerTest.echoBack"]("hello from client")
        print(f"Call to all remotes result: {result}")
    except Exception as e:
        print(f"Error calling server method: {e}")
    
    # Keep running for a while
    await asyncio.sleep(10)
    
    # Cleanup
    await client.disconnect()
    await server.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped by user")

#!/usr/bin/env python3
"""
Example JSON-RPC server with a Calculator class for testing
"""
import asyncio
from jrpc_server import JRPCServer


class Calculator:
    """A simple calculator class for testing RPC"""
    def add(self, a, b):
        """Add two numbers"""
        return a + b

    def subtract(self, a, b):
        """Subtract b from a"""
        return a - b

    def multiply(self, a, b):
        """Multiply two numbers"""
        return a * b


if __name__ == "__main__":    
    # Create server
    server = JRPCServer()
    
    # Register calculator instance
    server.register_instance(Calculator())
    
    # Start server
    print(f"Starting WebSocket RPC server on ws://{server.host}:{server.port}")
    asyncio.get_event_loop().run_until_complete(server.start())
    asyncio.get_event_loop().run_forever()

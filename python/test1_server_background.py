#!/usr/bin/env python3
"""
Test 1: Client-to-Server RPC test server using background mode
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from python.jrpc_server import JRPCServer

class Calculator:
    """A calculator class for testing client-to-server calls"""
    def __init__(self):
        self.operations = []
        
    async def add(self, a, b):
        result = a + b
        return result

    async def subtract(self, a, b):
        result = a - b
        return result

    async def multiply(self, a, b):
        result = a * b
        return result

async def some_background_work():
    """Simulate other async work happening while server runs"""
    counter = 0
    while True:
        print(f"Background work iteration {counter}")
        counter += 1
        await asyncio.sleep(2)  # Sleep for 2 seconds

def main():
    # Setup server
    server = JRPCServer(port=8080, debug=False)
    calc = Calculator()
    server.add_class(calc)
    
    print("Test 1 - Starting Calculator Server on port 8080 in background...")
    
    # Start server in background thread
    server_thread = server.run_in_thread()
    
    try:
        counter = 0
        while True:
            print(f"Background work iteration {counter}")
            counter += 1
            import time
            time.sleep(2)  # Using time.sleep since we're in a regular thread now
            
    except KeyboardInterrupt:
        print("\nShutting down calculator server...")

if __name__ == "__main__":
    main()

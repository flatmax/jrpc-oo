#!/usr/bin/env python3
"""
Cross-language interop test: Python client exposing methods for JS server to call.

Usage:
1. Start JS server: node tests/JRPCServerTestInterop.js
2. Run this client: python jrpc_oo/tests/test_interop_js_server_reverse.py

Expected: JS server can call Python client methods and receive correct responses.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from jrpc_oo.JRPCClient import JRPCClient


class PythonTestClient:
    """Client class exposing methods for JS server to call."""
    
    def python_echo(self, message):
        """Echo from Python client."""
        print(f"Python: python_echo called with: {message}")
        return f"python_echo: {message}"
    
    def get_client_type(self):
        """Identify this client."""
        print("Python: get_client_type called")
        return "python"
    
    def echo_data(self, data):
        """Echo complex data back."""
        print(f"Python: echo_data called with: {data}")
        return data


async def run_client():
    """Connect to JS server and wait for it to call our methods."""
    print("=" * 60)
    print("Cross-Language Interop Test: JS Server → Python Client")
    print("=" * 60)
    print()
    print("Connecting to ws://127.0.0.1:9000...")
    
    client = JRPCClient("ws://127.0.0.1:9000")
    test_class = PythonTestClient()
    client.add_class(test_class, "PythonTestClient")
    
    # Start connection in background
    connect_task = asyncio.create_task(client.connect())
    
    # Wait for connection
    connected = False
    for _ in range(50):  # 5 second timeout
        await asyncio.sleep(0.1)
        if client.connected and client.server:
            connected = True
            break
    
    if not connected:
        print("FAILED: Could not connect to JS server")
        print("Make sure JS server is running: node tests/JRPCServerTestInterop.js")
        return False
    
    print("Connected!")
    print("Exposed methods for JS server to call:")
    print("  - PythonTestClient.python_echo")
    print("  - PythonTestClient.get_client_type")
    print("  - PythonTestClient.echo_data")
    print()
    print("Waiting for JS server to call methods...")
    print()
    
    # Stay connected for JS server to run its tests
    await asyncio.sleep(10)
    
    # Cleanup
    await client.disconnect()
    connect_task.cancel()
    try:
        await connect_task
    except asyncio.CancelledError:
        pass
    
    print()
    print("Python client finished")
    return True


if __name__ == "__main__":
    asyncio.run(run_client())

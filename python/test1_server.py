#!/usr/bin/env python3
"""
Test 1: Client-to-Server RPC test server
"""
from jrpc_server import JRPCServer

class Calculator:
    """A calculator class for testing client-to-server calls"""
    def __init__(self):
        self.operations = []
        
    def add(self, a, b):
        result = a + b
        return result

    def subtract(self, a, b):
        result = a - b
        return result

    def multiply(self, a, b):
        result = a * b
        return result

if __name__ == "__main__":    
    server = JRPCServer(port=8080)
    calc = Calculator()
    server.add_class(calc)
    
    print("Test 1 - Starting Calculator Server on port 8080...")
    try:
        server.start()
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down calculator server...")

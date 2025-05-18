#!/usr/bin/env python3
"""
Example JRPC client for testing the Python implementation.
Similar to Client2.js
"""

import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from JRPCClient import JRPCClient

class TestClass:
    def uniqueFn2(self, i, str_param=None):
        """Unique function for client 2"""
        print('unique2')
        print('args:', i, str_param)
        return i + 1
    
    def commonFn(self, *args):
        """Common function implemented by both clients"""
        print('args:', args)
        return 'Client 2'

if __name__ == "__main__":
    # Create client connecting to server on port 9000
    jrpc_client = JRPCClient(server_uri='ws://localhost:9000')
    
    # Create test class instance and add it
    tc = TestClass()
    jrpc_client.add_class(tc)
    
    # Keep the client running
    try:
        print("Client 2 running. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nClosing client")
        jrpc_client.close()

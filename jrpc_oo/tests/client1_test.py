#!/usr/bin/env python3
"""
Example JRPC client for testing the Python implementation.
Similar to Client1.js
"""

import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from jrpc_oo.JRPCClient import JRPCClient

class TestClass:
    def uniqueFn1(self, i, str_param):
        """Unique function for client 1"""
        print('unique1')
        print('args:', i, str_param)
        return i + 1
    
    def commonFn(self, i, str_param=None):
        """Common function implemented by both clients"""
        print('commonFn called with:', i, str_param)
        return 'Client 1'

if __name__ == "__main__":
    # Create client connecting to server on port 9000
    jrpc_client = JRPCClient(server_uri='ws://localhost:9000')
    
    # Create test class instance and add it
    tc = TestClass()
    jrpc_client.add_class(tc)
    
    # Keep the client running
    try:
        print("Client 1 running. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nClosing client")
        jrpc_client.close()

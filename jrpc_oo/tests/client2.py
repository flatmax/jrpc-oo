"""
Test client 2 for JRPC-OO Python implementation.
Similar to Client2.js
"""

import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from JRPCClient import JRPCClient

class TestClass:
    """Test class with methods to expose over RPC."""
    
    def uniqueFn2(self, i):
        """Second unique test function."""
        print("unique2")
        print(i)
        return i + 1
    
    def commonFn(self):
        """Common function implemented by both clients."""
        print(sys.argv)
        return "Client 2"

if __name__ == "__main__":
    # Connect to server
    jrnc = JRPCClient('wss://0.0.0.0:9000')
    jrnc.connect()
    
    # Create test class instance
    tc = TestClass()
    
    # Add the class to expose its methods over RPC
    jrnc.add_class(tc)
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Client stopped")

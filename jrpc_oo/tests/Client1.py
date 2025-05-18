"""
Python equivalent of the Client1.js test file.
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from jrpc_oo.JRPCClient import JRPCClient

class TestClass:
    """Test class with methods to expose via JRPC."""
    
    def uniqueFn1(self, i, message):
        """Equivalent to the JavaScript uniqueFn1 method."""
        print('unique1')
        print(f'Arguments: {i}, {message}')
        return i + 1
    
    def commonFn(self):
        """Common function implemented by both clients."""
        print('commonFn called on Client 1')
        return 'Client 1'


async def main():
    """Main function to set up the client."""
    client = JRPCClient('ws://0.0.0.0:9000')
    
    # Create test class instance and expose it
    tc = TestClass()
    client.add_class(tc)
    
    # Connect to server
    await client.connect()
    
    # Keep client running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Client stopped by user")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

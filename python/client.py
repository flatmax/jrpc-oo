#!/usr/bin/env python3
"""
Example JSON-RPC client with bidirectional capability
"""
import asyncio
from jrpc_client import JRPCClient

class Display:
    """Display class that server can call to show results"""
    def show(self, text):
        """Display text sent from server"""
        print("\nServer sent calculation history:")
        print(text)
        return True

async def main():
    client = JRPCClient()
    
    try:
        # Register Display instance for server callbacks
        display = Display()
        client.register_instance(display)
        
        # Connect and get Calculator proxy
        await client.connect()
        calc = client['Calculator']
        
        # Make some calculations
        print("\nMaking calculations...")
        await calc.add(5, 3)
        await calc.subtract(10, 4) 
        await calc.multiply(6, 7)
        
        # Ask server to show history
        print("\nRequesting calculation history...")
        count = await calc.show_history()
        print(f"Server showed {count} calculations")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())

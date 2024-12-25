#!/usr/bin/env python3
"""
Example JSON-RPC server with Calculator class and bidirectional calling capability
"""
import asyncio
from jrpc_server import JRPCServer

class Calculator:
    """A calculator class that uses remote display to show results"""
    def __init__(self):
        self.operations = []
        
    def add(self, a, b):
        """Add two numbers and display result"""
        result = a + b
        # Store operation for later display
        self.operations.append(f"{a} + {b} = {result}")
        return result

    def subtract(self, a, b):
        """Subtract b from a and display result"""
        result = a - b
        self.operations.append(f"{a} - {b} = {result}")
        return result

    def multiply(self, a, b):
        """Multiply two numbers and display result"""
        result = a * b
        self.operations.append(f"{a} * {b} = {result}")
        return result
        
    async def show_history(self):
        """Show calculation history using client's display"""
        # This will call back to the client's Display.show method
        for remote_id, websocket in self.get_remotes().items():
            await self.call_remote(websocket, "Display.show", 
                               ["\n".join(self.operations)])
        return len(self.operations)

if __name__ == "__main__":    
    # Create server
    server = JRPCServer()
    
    # Create calculator instance
    calc = Calculator()
    
    # Give calculator access to RPC methods
    calc.get_remotes = lambda: server.remotes
    calc.call_remote = server.call_remote
    
    # Register calculator instance
    server.register_instance(calc)
    
    # Start server
    print(f"Starting WebSocket RPC server on ws://{server.host}:{server.port}")
    async def main():
        await server.start()
        await asyncio.Future()  # run forever
        
    asyncio.run(main())

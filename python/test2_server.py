#!/usr/bin/env python3
"""
Test 2: Server-to-Client RPC test server
"""
import asyncio
from jrpc_server import JRPCServer

class NotificationServer:
    """Server-side notification handler"""
    def __init__(self):
        self.clients = []

    async def register_client(self, _):
        """Register a client for notifications"""
        print("Client registered for notifications")
        return True

class NotificationTestServer(JRPCServer):
    """A server that sends notifications to client after connection"""
    
    def __init__(self, port=8082, debug=True):
        super().__init__(port=port, debug=debug)
        self.notifier = NotificationServer()
        self.add_class(self.notifier)
    
    async def handle_client(self, websocket, path):
        """Override handle_client to send messages after connection setup"""
        self.ws = websocket
        print(f"New client connected")
        
        # Start message processing in background task
        process_messages_task = asyncio.create_task(
            self.process_incoming_messages(websocket)
        )
        
        try:
            # Do component discovery
            await self.discover_components()
            print("Components discovered:", self.remotes)
            
            # Wait for client registration
            await asyncio.sleep(0.1)  # Give client time to register
            
            # Start sending notifications
            await self._send_notifications()
            
            # Keep connection alive
            await process_messages_task
            
        except Exception as e:
            print(f"Error in handle_client: {e}")
    
    async def _send_notifications(self):
        """Send test messages to client"""
        if "Display.show" not in self.remotes:
            print("Error: Display.show not found in client components")
            return

        messages = [
            "Test message #1",
            "Test message #2", 
            "Test message #3"
        ]
        
        for msg in messages:
            await asyncio.sleep(1)  # Pause between messages
            try:
                await self.call_method("Display.show", {"args": [msg]})
                print(f"Server sent '{msg}'")
            except Exception as e:
                print(f"Server Failed to send '{msg}': {e}")

if __name__ == "__main__":    
    server = NotificationTestServer(port=8082, debug=True)
    
    print("Test 2 - Starting Notification Server on port 8082...")
    try:
        print("Starting server...")
        server.start()
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down notification server...")

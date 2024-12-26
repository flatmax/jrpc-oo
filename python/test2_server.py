#!/usr/bin/env python3
"""
Test 2: Server-to-Client RPC test server
"""
import json
import asyncio
from jrpc_server import JRPCServer

class NotificationServer:
    """A server that sends notifications to client"""
    def __init__(self):
        self.rpc = None
        
    def set_rpc(self, rpc):
        """Store RPC instance for making calls back to client"""
        self.rpc = rpc
    
    async def register_client(self, _):
        """Called by client to indicate it's ready for notifications"""
        if not self.rpc:
            print("Server: No RPC connection available")
            return False
            
        # Start sending notifications asynchronously
        asyncio.create_task(self._send_notifications())
        return True
    
    async def _send_notifications(self):
        """Send notifications to registered client"""
        messages = [
            "Test message #1",
            "Test message #2", 
            "Test message #3"
        ]
        
        for msg in messages:
            await asyncio.sleep(1)  # Pause between messages
            try:
                # Create and send request through websocket
                request = {
                    'jsonrpc': '2.0',
                    'method': 'Display.show',
                    'params': [msg],
                    'id': None  # Notification doesn't need an ID
                }
                await self.rpc.ws.send(json.dumps(request))
                print(f"Server sent '{msg}'")
            except Exception as e:
                print(f"Server Failed to send '{msg}': {e}")

if __name__ == "__main__":    
    server = JRPCServer(port=8082, debug=False)
    notifier = NotificationServer()
    server.add_class(notifier)
    
    print("Test 2 - Starting Notification Server on port 8082...")
    try:
        print("Starting server...")
        server.start()
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down notification server...")

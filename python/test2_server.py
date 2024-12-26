#!/usr/bin/env python3
"""
Test 2: Server-to-Client RPC test server
"""
from jrpc_server import JRPCServer
import time

class NotificationServer:
    """A server that sends notifications to client"""
    def __init__(self):
        self.client = None
    
    def start_notifications(self):
        """Start sending notifications to client"""
        if not self.client:
            return False
            
        print("\nServer starting notifications...")
        messages = [
            "Test message #1",
            "Test message #2",
            "Test message #3"
        ]
        
        for msg in messages:
            time.sleep(1)  # Pause between messages
            try:
                success = self.client.Display.show(msg)
                print(f"Server sent: '{msg}', Client responded: {success}")
            except Exception as e:
                print(f"Failed to send '{msg}': {e}")
                
        return True

if __name__ == "__main__":    
    server = JRPCServer(port=8082)
    notifier = NotificationServer()
    notifier.client = server.client
    server.register_instance(notifier)
    
    print("Test 2 - Starting Notification Server on port 8082...")
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down notification server...")
